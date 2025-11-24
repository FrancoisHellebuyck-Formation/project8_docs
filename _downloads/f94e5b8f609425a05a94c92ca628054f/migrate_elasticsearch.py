#!/usr/bin/env python3
"""
Script de migration Elasticsearch et Kibana.

Ce script permet de:
1. Exporter/Importer les index Elasticsearch
2. Exporter/Importer les dataviews (index patterns) Kibana
3. Exporter/Importer les dashboards Kibana
4. Sauvegarder/Restaurer l'ensemble de la configuration

Usage:
    # Export complet
    python scripts/migrate_elasticsearch.py export --output ./backup

    # Import complet
    python scripts/migrate_elasticsearch.py import --input ./backup

    # Export uniquement les index
    python scripts/migrate_elasticsearch.py export-indexes --output ./backup

    # Export uniquement les dashboards
    python scripts/migrate_elasticsearch.py export-dashboards --output ./backup

    # Migration directe (source → destination)
    python scripts/migrate_elasticsearch.py migrate \\
        --source-host localhost:9200 \\
        --dest-host production:9200

Requirements:
    pip install elasticsearch requests
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from elasticsearch import Elasticsearch
    import requests
except ImportError:
    print("❌ Modules manquants. Installez-les avec:")
    print("   uv pip install elasticsearch requests")
    sys.exit(1)


class ElasticsearchMigrator:
    """Gestionnaire de migration Elasticsearch/Kibana."""

    def __init__(
        self,
        es_host: str = "localhost:9200",
        kibana_host: str = "localhost:5601",
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initialise le migrateur.

        Args:
            es_host: Hôte Elasticsearch (host:port)
            kibana_host: Hôte Kibana (host:port)
            username: Nom d'utilisateur (optionnel)
            password: Mot de passe (optionnel)
        """
        self.es_host = es_host
        self.kibana_host = kibana_host

        # Connexion Elasticsearch
        if username and password:
            self.es = Elasticsearch(
                [f"http://{es_host}"], basic_auth=(username, password)
            )
        else:
            self.es = Elasticsearch([f"http://{es_host}"])

        # URL Kibana
        self.kibana_url = f"http://{kibana_host}"
        self.auth = (username, password) if username and password else None

        print(f"✅ Connecté à Elasticsearch: {es_host}")
        print(f"✅ Connecté à Kibana: {kibana_host}")

    # ============= EXPORT INDEX =============

    def export_indexes(
        self, output_dir: Path, index_patterns: List[str] = None
    ) -> Dict:
        """
        Export les index Elasticsearch.

        Args:
            output_dir: Répertoire de sortie
            index_patterns: Patterns d'index à exporter (défaut: ml-api-*)

        Returns:
            Dict avec statistiques d'export
        """
        if index_patterns is None:
            index_patterns = ["ml-api-*"]

        output_dir = Path(output_dir) / "indexes"
        output_dir.mkdir(parents=True, exist_ok=True)

        stats = {"exported": 0, "documents": 0, "errors": []}

        print("\n📦 Export des index Elasticsearch...")

        for pattern in index_patterns:
            indexes = self.es.indices.get(index=pattern)

            for index_name, index_info in indexes.items():
                print(f"\n  → Export de l'index: {index_name}")

                try:
                    # Export mapping
                    mapping_file = output_dir / f"{index_name}_mapping.json"
                    with open(mapping_file, "w") as f:
                        json.dump(index_info, f, indent=2)
                    print(f"    ✓ Mapping sauvegardé: {mapping_file}")

                    # Export documents
                    docs_file = output_dir / f"{index_name}_documents.ndjson"
                    doc_count = 0

                    # Scroll pour récupérer tous les documents
                    response = self.es.search(
                        index=index_name,
                        scroll="2m",
                        size=1000,
                        body={"query": {"match_all": {}}},
                    )

                    scroll_id = response["_scroll_id"]
                    hits = response["hits"]["hits"]

                    with open(docs_file, "w") as f:
                        while hits:
                            for hit in hits:
                                # Format NDJSON pour réimport facile
                                doc = {
                                    "index": {"_index": index_name, "_id": hit["_id"]}
                                }
                                f.write(json.dumps(doc) + "\n")
                                f.write(json.dumps(hit["_source"]) + "\n")
                                doc_count += 1

                            response = self.es.scroll(scroll_id=scroll_id, scroll="2m")
                            scroll_id = response["_scroll_id"]
                            hits = response["hits"]["hits"]

                    self.es.clear_scroll(scroll_id=scroll_id)

                    print(f"    ✓ {doc_count} documents exportés: {docs_file}")

                    stats["exported"] += 1
                    stats["documents"] += doc_count

                except Exception as e:
                    error_msg = f"Erreur lors de l'export de {index_name}: {e}"
                    print(f"    ✗ {error_msg}")
                    stats["errors"].append(error_msg)

        print(
            f"\n✅ Export terminé: {stats['exported']} index, "
            f"{stats['documents']} documents"
        )
        return stats

    # ============= IMPORT INDEX =============

    def import_indexes(self, input_dir: Path) -> Dict:
        """
        Import les index Elasticsearch.

        Args:
            input_dir: Répertoire contenant les exports

        Returns:
            Dict avec statistiques d'import
        """
        input_dir = Path(input_dir) / "indexes"
        stats = {"imported": 0, "documents": 0, "errors": []}

        print("\n📥 Import des index Elasticsearch...")

        # Trouver tous les fichiers de mapping
        mapping_files = list(input_dir.glob("*_mapping.json"))

        for mapping_file in mapping_files:
            index_name = mapping_file.stem.replace("_mapping", "")
            docs_file = input_dir / f"{index_name}_documents.ndjson"

            print(f"\n  → Import de l'index: {index_name}")

            try:
                # Créer l'index avec mapping
                with open(mapping_file) as f:
                    index_config = json.load(f)

                if self.es.indices.exists(index=index_name):
                    print(f"    ⚠️  Index {index_name} existe déjà, " "suppression...")
                    self.es.indices.delete(index=index_name)

                self.es.indices.create(index=index_name, body=index_config)
                print("    ✓ Index créé avec mapping")

                # Import documents
                if docs_file.exists():
                    doc_count = 0
                    batch = []

                    with open(docs_file) as f:
                        lines = f.readlines()
                        for i in range(0, len(lines), 2):
                            if i + 1 < len(lines):
                                batch.append(lines[i])
                                batch.append(lines[i + 1])
                                doc_count += 1

                                # Bulk insert par batch de 1000
                                if len(batch) >= 2000:
                                    self.es.bulk(body="".join(batch), refresh=True)
                                    batch = []

                    # Dernier batch
                    if batch:
                        self.es.bulk(body="".join(batch), refresh=True)

                    print(f"    ✓ {doc_count} documents importés")
                    stats["documents"] += doc_count

                stats["imported"] += 1

            except Exception as e:
                error_msg = f"Erreur lors de l'import de {index_name}: {e}"
                print(f"    ✗ {error_msg}")
                stats["errors"].append(error_msg)

        print(
            f"\n✅ Import terminé: {stats['imported']} index, "
            f"{stats['documents']} documents"
        )
        return stats

    # ============= EXPORT DATAVIEWS =============

    def export_dataviews(self, output_dir: Path) -> Dict:
        """
        Export les dataviews (index patterns) Kibana.

        Args:
            output_dir: Répertoire de sortie

        Returns:
            Dict avec statistiques d'export
        """
        output_dir = Path(output_dir) / "dataviews"
        output_dir.mkdir(parents=True, exist_ok=True)

        stats = {"exported": 0, "errors": []}

        print("\n📊 Export des dataviews Kibana...")

        try:
            # API Kibana pour récupérer les index patterns
            url = f"{self.kibana_url}/api/saved_objects/_find"
            params = {"type": "index-pattern", "per_page": 1000}

            response = requests.get(url, params=params, auth=self.auth)
            response.raise_for_status()

            data = response.json()
            dataviews = data.get("saved_objects", [])

            for dataview in dataviews:
                dataview_id = dataview["id"]
                dataview_title = dataview["attributes"]["title"]

                # Sauvegarder chaque dataview
                output_file = output_dir / f"{dataview_id}.json"
                with open(output_file, "w") as f:
                    json.dump(dataview, f, indent=2)

                print(f"  ✓ Dataview exporté: {dataview_title}")
                stats["exported"] += 1

            print(f"\n✅ {stats['exported']} dataviews exportés")

        except Exception as e:
            error_msg = f"Erreur lors de l'export des dataviews: {e}"
            print(f"  ✗ {error_msg}")
            stats["errors"].append(error_msg)

        return stats

    # ============= IMPORT DATAVIEWS =============

    def import_dataviews(self, input_dir: Path) -> Dict:
        """
        Import les dataviews Kibana.

        Args:
            input_dir: Répertoire contenant les exports

        Returns:
            Dict avec statistiques d'import
        """
        input_dir = Path(input_dir) / "dataviews"
        stats = {"imported": 0, "errors": []}

        print("\n📊 Import des dataviews Kibana...")

        dataview_files = list(input_dir.glob("*.json"))

        for dataview_file in dataview_files:
            try:
                with open(dataview_file) as f:
                    dataview = json.load(f)

                dataview_id = dataview["id"]
                dataview_title = dataview["attributes"]["title"]

                # API Kibana pour créer/mettre à jour
                url = f"{self.kibana_url}/api/saved_objects/index-pattern/{dataview_id}"  # noqa: E501
                headers = {
                    "kbn-xsrf": "true",
                    "Content-Type": "application/json",
                }  # noqa: E501

                response = requests.post(
                    url, json=dataview, headers=headers, auth=self.auth
                )

                if response.status_code in [200, 201]:
                    print(f"  ✓ Dataview importé: {dataview_title}")
                    stats["imported"] += 1
                else:
                    raise Exception(f"HTTP {response.status_code}: " f"{response.text}")

            except Exception as e:
                error_msg = f"Erreur lors de l'import de {dataview_file.name}: {e}"  # noqa: E501
                print(f"  ✗ {error_msg}")
                stats["errors"].append(error_msg)

        print(f"\n✅ {stats['imported']} dataviews importés")
        return stats

    # ============= EXPORT DASHBOARDS =============

    def export_dashboards(self, output_dir: Path) -> Dict:
        """
        Export les dashboards Kibana.

        Args:
            output_dir: Répertoire de sortie

        Returns:
            Dict avec statistiques d'export
        """
        output_dir = Path(output_dir) / "dashboards"
        output_dir.mkdir(parents=True, exist_ok=True)

        stats = {"exported": 0, "errors": []}

        print("\n📈 Export des dashboards Kibana...")

        try:
            # API Kibana pour récupérer les dashboards
            url = f"{self.kibana_url}/api/saved_objects/_find"
            params = {"type": "dashboard", "per_page": 1000}

            response = requests.get(url, params=params, auth=self.auth)
            response.raise_for_status()

            data = response.json()
            dashboards = data.get("saved_objects", [])

            for dashboard in dashboards:
                dashboard_id = dashboard["id"]
                dashboard_title = dashboard["attributes"]["title"]

                # Sauvegarder chaque dashboard
                output_file = output_dir / f"{dashboard_id}.json"
                with open(output_file, "w") as f:
                    json.dump(dashboard, f, indent=2)

                print(f"  ✓ Dashboard exporté: {dashboard_title}")
                stats["exported"] += 1

            # Export aussi les visualisations associées
            viz_url = f"{self.kibana_url}/api/saved_objects/_find"
            viz_params = {"type": "visualization", "per_page": 1000}

            viz_response = requests.get(viz_url, params=viz_params, auth=self.auth)
            viz_response.raise_for_status()

            viz_data = viz_response.json()
            visualizations = viz_data.get("saved_objects", [])

            viz_dir = output_dir / "visualizations"
            viz_dir.mkdir(exist_ok=True)

            for viz in visualizations:
                viz_id = viz["id"]
                viz_title = viz["attributes"]["title"]

                output_file = viz_dir / f"{viz_id}.json"
                with open(output_file, "w") as f:
                    json.dump(viz, f, indent=2)

                print(f"  ✓ Visualisation exportée: {viz_title}")
                stats["exported"] += 1

            print(f"\n✅ {stats['exported']} dashboards/visualisations " "exportés")

        except Exception as e:
            error_msg = f"Erreur lors de l'export des dashboards: {e}"
            print(f"  ✗ {error_msg}")
            stats["errors"].append(error_msg)

        return stats

    # ============= IMPORT DASHBOARDS =============

    def import_dashboards(self, input_dir: Path) -> Dict:
        """
        Import les dashboards Kibana.

        Args:
            input_dir: Répertoire contenant les exports

        Returns:
            Dict avec statistiques d'import
        """
        input_dir = Path(input_dir) / "dashboards"
        stats = {"imported": 0, "errors": []}

        print("\n📈 Import des dashboards Kibana...")

        # Importer d'abord les visualisations
        viz_dir = input_dir / "visualizations"
        if viz_dir.exists():
            viz_files = list(viz_dir.glob("*.json"))

            for viz_file in viz_files:
                try:
                    with open(viz_file) as f:
                        viz = json.load(f)

                    viz_id = viz["id"]
                    viz_title = viz["attributes"]["title"]

                    url = f"{self.kibana_url}/api/saved_objects/visualization/{viz_id}"  # noqa: E501
                    headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}

                    response = requests.post(
                        url, json=viz, headers=headers, auth=self.auth
                    )

                    if response.status_code in [200, 201]:
                        print(f"  ✓ Visualisation importée: {viz_title}")
                        stats["imported"] += 1
                    else:
                        raise Exception(
                            f"HTTP {response.status_code}: " f"{response.text}"
                        )

                except Exception as e:
                    error_msg = (
                        f"Erreur lors de l'import de {viz_file.name}: {e}"  # noqa: E501
                    )
                    print(f"  ✗ {error_msg}")
                    stats["errors"].append(error_msg)

        # Importer les dashboards
        dashboard_files = [f for f in input_dir.glob("*.json")]

        for dashboard_file in dashboard_files:
            try:
                with open(dashboard_file) as f:
                    dashboard = json.load(f)

                dashboard_id = dashboard["id"]
                dashboard_title = dashboard["attributes"]["title"]

                url = f"{self.kibana_url}/api/saved_objects/dashboard/{dashboard_id}"  # noqa: E501
                headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}

                response = requests.post(
                    url, json=dashboard, headers=headers, auth=self.auth
                )

                if response.status_code in [200, 201]:
                    print(f"  ✓ Dashboard importé: {dashboard_title}")
                    stats["imported"] += 1
                else:
                    raise Exception(f"HTTP {response.status_code}: " f"{response.text}")

            except Exception as e:
                error_msg = f"Erreur lors de l'import de {dashboard_file.name}: {e}"  # noqa: E501
                print(f"  ✗ {error_msg}")
                stats["errors"].append(error_msg)

        print(f"\n✅ {stats['imported']} dashboards/visualisations importés")
        return stats

    # ============= EXPORT COMPLET =============

    def export_all(self, output_dir: Path) -> Dict:
        """
        Export complet: index, dataviews, dashboards.

        Args:
            output_dir: Répertoire de sortie

        Returns:
            Dict avec statistiques globales
        """
        output_dir = Path(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = output_dir / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n🚀 Export complet vers: {backup_dir}\n")
        print("=" * 60)

        stats = {
            "timestamp": timestamp,
            "backup_dir": str(backup_dir),
            "indexes": self.export_indexes(backup_dir),
            "dataviews": self.export_dataviews(backup_dir),
            "dashboards": self.export_dashboards(backup_dir),
        }

        # Sauvegarder les stats
        stats_file = backup_dir / "migration_stats.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)

        print("\n" + "=" * 60)
        print("\n✅ Export complet terminé!")
        print(f"📁 Backup sauvegardé dans: {backup_dir}")
        print(f"📊 Statistiques: {stats_file}")

        return stats

    # ============= IMPORT COMPLET =============

    def import_all(self, input_dir: Path) -> Dict:
        """
        Import complet: index, dataviews, dashboards.

        Args:
            input_dir: Répertoire contenant le backup

        Returns:
            Dict avec statistiques globales
        """
        input_dir = Path(input_dir)

        print(f"\n🚀 Import complet depuis: {input_dir}\n")
        print("=" * 60)

        stats = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "source_dir": str(input_dir),
            "indexes": self.import_indexes(input_dir),
            "dataviews": self.import_dataviews(input_dir),
            "dashboards": self.import_dashboards(input_dir),
        }

        print("\n" + "=" * 60)
        print("\n✅ Import complet terminé!")

        return stats


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Migration Elasticsearch et Kibana",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Export complet
  python scripts/migrate_elasticsearch.py export --output ./backup

  # Import complet
  python scripts/migrate_elasticsearch.py import --input ./backup/backup_20250121_153000  # noqa: E501

  # Export uniquement les index
  python scripts/migrate_elasticsearch.py export-indexes --output ./backup

  # Avec authentification
  python scripts/migrate_elasticsearch.py export \\
    --output ./backup \\
    --username elastic \\
    --password changeme
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commande")

    # Export complet
    export_parser = subparsers.add_parser("export", help="Export complet")
    export_parser.add_argument("--output", required=True, help="Répertoire de sortie")

    # Import complet
    import_parser = subparsers.add_parser("import", help="Import complet")
    import_parser.add_argument("--input", required=True, help="Répertoire du backup")

    # Export index
    export_idx_parser = subparsers.add_parser(
        "export-indexes", help="Export uniquement les index"
    )
    export_idx_parser.add_argument(
        "--output", required=True, help="Répertoire de sortie"
    )

    # Import index
    import_idx_parser = subparsers.add_parser(
        "import-indexes", help="Import uniquement les index"
    )
    import_idx_parser.add_argument(
        "--input", required=True, help="Répertoire du backup"
    )

    # Export dataviews
    export_dv_parser = subparsers.add_parser(
        "export-dataviews", help="Export uniquement les dataviews"
    )
    export_dv_parser.add_argument(
        "--output", required=True, help="Répertoire de sortie"
    )

    # Import dataviews
    import_dv_parser = subparsers.add_parser(
        "import-dataviews", help="Import uniquement les dataviews"
    )
    import_dv_parser.add_argument("--input", required=True, help="Répertoire du backup")

    # Export dashboards
    export_db_parser = subparsers.add_parser(
        "export-dashboards", help="Export uniquement les dashboards"
    )
    export_db_parser.add_argument(
        "--output", required=True, help="Répertoire de sortie"
    )

    # Import dashboards
    import_db_parser = subparsers.add_parser(
        "import-dashboards", help="Import uniquement les dashboards"
    )
    import_db_parser.add_argument("--input", required=True, help="Répertoire du backup")

    # Arguments communs
    for p in [
        export_parser,
        import_parser,
        export_idx_parser,
        import_idx_parser,
        export_dv_parser,
        import_dv_parser,
        export_db_parser,
        import_db_parser,
    ]:
        p.add_argument(
            "--es-host",
            default="localhost:9200",
            help="Hôte Elasticsearch (défaut: localhost:9200)",
        )
        p.add_argument(
            "--kibana-host",
            default="localhost:5601",
            help="Hôte Kibana (défaut: localhost:5601)",
        )
        p.add_argument("--username", help="Nom d'utilisateur (optionnel)")
        p.add_argument("--password", help="Mot de passe (optionnel)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Créer le migrateur
    migrator = ElasticsearchMigrator(
        es_host=args.es_host,
        kibana_host=args.kibana_host,
        username=args.username,
        password=args.password,
    )

    # Exécuter la commande
    try:
        if args.command == "export":
            migrator.export_all(Path(args.output))
        elif args.command == "import":
            migrator.import_all(Path(args.input))
        elif args.command == "export-indexes":
            migrator.export_indexes(Path(args.output))
        elif args.command == "import-indexes":
            migrator.import_indexes(Path(args.input))
        elif args.command == "export-dataviews":
            migrator.export_dataviews(Path(args.output))
        elif args.command == "import-dataviews":
            migrator.import_dataviews(Path(args.input))
        elif args.command == "export-dashboards":
            migrator.export_dashboards(Path(args.output))
        elif args.command == "import-dashboards":
            migrator.import_dashboards(Path(args.input))

    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
