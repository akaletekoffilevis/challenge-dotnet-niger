# NextDev Challenge - Hébergement .NET 9

Ce projet représente le défi NextDev visant à héberger une application .NET 9 avec :
- Un site vitrine réalisé avec Razor Pages
- Une API minimaliste avec Swagger
- Une infrastructure réseau complète (DNS, DHCP, Apache en reverse proxy)

## Structure du projet

- `sites/www.nextdev.ne` : Projet Razor Pages (site vitrine)
- `sites/api.nextdev.ne` : Projet API Minimal (avec SQLite et Swagger)
- `docs` : Documentation supplémentaire
- `generate-pptx.py` : Script de génération de présentation
- `plan.md` : Feuille de route détaillée du défi
- `presentation.pptx` : Présentation du projet

## Architecture

```
Client Web ──► www.nextdev.ne ──► Apache (port 80/443)
                                        │
                                        ├── ProxyPass ──► Kestrel :5000 (Razor Pages)
                                        │
Client API ──► api.nextdev.ne ──► Apache (port 80/443)
                                        │
                                        └── ProxyPass ──► Kestrel :5001 (Minimal API)
                                                                 │
                                                                 └── SQLite (trainees.db)
```

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.