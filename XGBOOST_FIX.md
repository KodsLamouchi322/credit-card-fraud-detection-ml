# Solution pour l'erreur "ModuleNotFoundError: No module named 'xgboost'"

## Problème
Le module xgboost est installé dans Anaconda mais le kernel Jupyter ne le trouve pas.

## Solutions

### Solution 1: Installer xgboost dans le kernel Jupyter actuel
Exécutez cette commande dans une cellule du notebook:

```python
import sys
!{sys.executable} -m pip install xgboost
```

### Solution 2: Utiliser le kernel Anaconda
1. Dans Jupyter, allez dans **Kernel** → **Change Kernel**
2. Sélectionnez le kernel Python d'Anaconda (généralement nommé "Python 3 (ipykernel)" ou "base")

### Solution 3: Installer xgboost via Anaconda
Ouvrez Anaconda Prompt et exécutez:

```bash
conda install -c conda-forge xgboost
```

### Solution 4: Redémarrer le kernel
Après l'installation, redémarrez le kernel Jupyter:
- **Kernel** → **Restart Kernel**

## Vérification
Pour vérifier que xgboost est bien installé, exécutez dans une cellule:

```python
import xgboost as xgb
print(f"XGBoost version: {xgb.__version__}")
```

## Alternative: Continuer sans XGBoost
Si vous ne souhaitez pas utiliser XGBoost, vous pouvez simplement sauter les cellules qui l'utilisent. Les modèles Logistic Regression et Random Forest fonctionneront parfaitement.
