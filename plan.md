# Challenge NextDev — Hébergement .NET 9

## Feuille de route (48h)

---

### Phase 1 : Infrastructure (H0 - H12)

#### 1.1 Installation de l'OS
- [x] Installer Ubuntu 26.04 LTS
- [x] Configurer les interfaces réseau (IP WiFi : 10.0.0.68)
- [x] Mettre à jour les paquets : `apt update && apt upgrade -y`
- [x] Installer les outils de base : `curl wget git nano ufw`

#### 1.2 Configuration DNS
- [x] Installer BIND9 : `apt install bind9`
- [x] Configurer la zone DNS pour `nextdev.ne`
- [x] Créer les enregistrements :
  - `www.nextdev.ne` → 10.0.0.68
  - `api.nextdev.ne` → 10.0.0.68
- [x] Tester la résolution avec `dig` / `nslookup`

#### 1.3 Configuration DHCP
- [x] Installer ISC DHCP Server : `apt install isc-dhcp-server`
- [x] Définir la plage d'adresses et bail (10.0.0.50 → 10.0.0.200)
- [x] Configurer les options DNS et gateway

#### 1.4 Installation d'Apache2
- [x] Installer Apache2 : `apt install apache2`
- [x] Activer les modules nécessaires : `proxy`, `proxy_http`, `rewrite`, `ssl`, `headers`, `deflate`, `expires`
- [x] Configurer les VirtualHosts pour :
  - `www.nextdev.ne` (port 80 → site Razor sur :5000)
  - `api.nextdev.ne` (port 80 → API sur :5001)
- [x] Configurer le pare-feu (UFW) : ouvrir les ports 80, 443, 53, 67

---

### Phase 2 : Développement .NET 9 (H12 - H24)

#### 2.1 Installation du SDK .NET 9
- [x] SDK .NET 9.0.313 déjà installé

#### 2.2 Projet Site Vitrine (Razor Pages)
- [x] Créer le projet : `dotnet new razor -n NextDev.Web -o sites/www.nextdev.ne`
- [x] Développer les pages : Accueil personnalisée "Bienvenue sur NextDev"
- [x] Thème Bootstrap responsive
- [x] Configurer le port d'écoute : 5000

#### 2.3 Projet API (Minimal API)
- [x] Créer le projet : `dotnet new webapi -n NextDev.Api -o sites/api.nextdev.ne`
- [x] Mettre en place SQLite :
  - Package `Microsoft.EntityFrameworkCore.Sqlite` 9.0.0
  - Modèle `Trainee` (Id, Nom, Prenom, Email, DateNaissance, DateInscription)
  - DbContext + DbSeeder
  - Base SQLite (nextdev.db)
- [x] Implémenter les endpoints :
  - `GET /` → page d'accueil de l'API
  - `GET /trainee` → liste des stagiaires (5 données démo)
- [x] Swagger UI accessible sur `/swagger`
- [x] Configurer le port d'écoute : 5001

#### 2.4 Test en local
- [x] Lancer les deux projets et tester avec `curl`
- [x] Vérifier que l'API retourne bien les données SQLite

---

### Phase 3 : Reverse Proxy & Intégration (H24 - H36)

#### 3.1 Configuration Apache Reverse Proxy
- [x] VirtualHost `www.nextdev.ne` → ProxyPass vers :5000
- [x] VirtualHost `api.nextdev.ne` → ProxyPass vers :5001

#### 3.2 Configuration SSL (HTTPS)
- [ ] Installer Certbot pour les certificats Let's Encrypt

#### 3.3 Intégration Base de Données
- [x] Données de démonstration : 5 stagiaires (Diop, Koné, Traoré, Ndiaye, Diallo)
- [ ] Afficher les stagiaires sur le site vitrine (optionnel)

#### 3.4 Script de démarrage
- [ ] Créer `start-all.sh` pour lancer les deux projets

---

### Phase 4 : Tests, Communication & Soutenance (H36 - H48)

#### 4.1 Tests fonctionnels
- [x] Tous les endpoints répondent (HTTP 200)
- [x] Résolution DNS fonctionnelle (dig)
- [x] Apache Reverse Proxy fonctionne sur les 2 domaines
- [ ] Endpoint `/trainee` retourne JSON

#### 4.2 Tests de résilience
- [ ] Redémarrer les services : les sites reviennent

#### 4.3 Préparation soutenance
- [ ] Réviser la présentation PPTX
- [ ] Préparer les réponses aux questions du jury

---

## Architecture cible (atteinte)

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

## URLs des endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `http://www.nextdev.ne` | GET | Site vitrine Razor Pages ✅ |
| `http://api.nextdev.ne` | GET | Accueil API ✅ |
| `http://api.nextdev.ne/trainee` | GET | Liste des stagiaires (JSON) ✅ |
| `http://api.nextdev.ne/swagger` | GET | Documentation Swagger ✅ |
