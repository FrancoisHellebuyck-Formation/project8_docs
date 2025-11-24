# Configuration du token HuggingFace pour les tests

Ce guide explique comment configurer votre token HuggingFace pour tester l'API Gradio sur un Space privé.

## 📋 Prérequis

- Un compte HuggingFace : https://huggingface.co/join
- Un Space HuggingFace déployé (public ou privé)

## 🔑 Étape 1 : Créer un token HuggingFace

1. Connectez-vous à HuggingFace : https://huggingface.co/login
2. Allez dans vos paramètres : https://huggingface.co/settings/tokens
3. Cliquez sur **"New token"**
4. Donnez un nom au token (ex: "API Testing")
5. Sélectionnez le type **"Read"** (lecture seule suffit pour les tests)
6. Cliquez sur **"Generate token"**
7. **Copiez le token** (il commence par `hf_`)

⚠️ **Important** : Conservez ce token en sécurité, il ne sera affiché qu'une seule fois !

## 📝 Étape 2 : Ajouter le token au fichier .env

1. Copiez le fichier d'exemple si vous ne l'avez pas encore fait :
   ```bash
   cp .env.example .env
   ```

2. Ouvrez le fichier `.env` et ajoutez votre token :
   ```bash
   # HuggingFace Token (pour accès aux Spaces privés)
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
   ```

3. Remplacez `hf_xxxxxxxxxxxxxxxxxxxxx` par votre token réel

## ✅ Étape 3 : Tester la configuration

### Test automatique via Makefile

Le Makefile charge automatiquement le token depuis `.env` :

```bash
make test-gradio-api-hf
```

Vous devriez voir :
```
Test de l'API Gradio (HuggingFace Spaces)...
URL: https://francoisformation-oc-project8.hf.space
Chargement de HF_TOKEN depuis .env...
🔐 Token HuggingFace: Configuré (Space privé)
```

### Test manuel

```bash
# Avec le token depuis .env
export $(cat .env | grep -v '^#' | grep HF_TOKEN | xargs)
GRADIO_URL=https://francoisformation-oc-project8.hf.space python test_gradio_api.py

# Ou directement avec la variable
HF_TOKEN=hf_xxxxx GRADIO_URL=https://francoisformation-oc-project8.hf.space python test_gradio_api.py
```

## 🔒 Sécurité

**Ne committez JAMAIS votre token dans Git !**

Le fichier `.env` est déjà dans `.gitignore` pour éviter cela. Vérifiez :

```bash
# Le token ne doit PAS apparaître dans git status
git status | grep .env

# Si .env apparaît, ajoutez-le au .gitignore
echo ".env" >> .gitignore
```

## 🌐 Space public vs privé

### Space PUBLIC (recommandé pour ce projet)

✅ Pas besoin de token  
✅ Accessible à tous  
✅ Parfait pour démonstrations et projets éducatifs  

Pour rendre votre Space public :
1. Allez sur https://huggingface.co/spaces/FrancoisFormation/oc-project8/settings
2. Section **"Visibility"**
3. Choisissez **"Public"**

### Space PRIVÉ

🔐 Nécessite un token HF  
🔒 Accessible uniquement avec authentification  
⚙️ Utile pour projets confidentiels  

## ❓ Dépannage

### Erreur "ValueError: Could not fetch config"

**Cause** : Le Space est privé et aucun token n'est fourni

**Solution** : Configurez `HF_TOKEN` dans `.env`

### Erreur "401 Client Error"

**Cause** : Token invalide ou expiré

**Solution** : 
1. Vérifiez que le token est correct dans `.env`
2. Générez un nouveau token si nécessaire

### Le token n'est pas chargé

**Vérification** :
```bash
# Vérifier le contenu du .env
grep HF_TOKEN .env

# Tester le chargement
export $(cat .env | grep -v '^#' | grep HF_TOKEN | xargs)
echo $HF_TOKEN
```

## 📚 Ressources

- Documentation HuggingFace Tokens : https://huggingface.co/docs/hub/security-tokens
- Documentation Gradio Client : https://www.gradio.app/guides/getting-started-with-the-python-client
- API Gradio de ce projet : README_HF.md

---

**Développé avec ❤️ dans le cadre du parcours MLOps OpenClassrooms**
