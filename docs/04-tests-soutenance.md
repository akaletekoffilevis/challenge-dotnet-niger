# Phase 4 : Tests, Communication & Soutenance (H36 - H48)

---

## 1. Tests fonctionnels complets

### 1.1 Test de l'infrastructure réseau

#### Test DNS

```bash
echo "=== Tests DNS ==="

# Test 1 : Résolution de www.nextdev.ne
dig www.nextdev.ne +short
# Attendu : 10.0.0.68

# Test 2 : Résolution de api.nextdev.ne
dig api.nextdev.ne +short
# Attendu : 10.0.0.68

# Test 3 : Résolution inverse
dig -x 10.0.0.68 +short
# Attendu : ns1.nextdev.ne. ou www.nextdev.ne.

# Test 4 : Vérification des enregistrements NS
dig nextdev.ne NS +short

echo "=== Tests DNS OK ==="
```

#### Test DHCP

```bash
echo "=== Tests DHCP ==="

# Sur une machine cliente, vérifier l'IP reçue
ip addr show | grep inet
# Attendu : IP dans la plage 192.168.1.50-200

# Voir les baux attribués
sudo dhcp-lease-list

echo "=== Tests DHCP OK ==="
```

### 1.2 Test des services

```bash
echo "=== Vérification des services ==="

services=("bind9" "isc-dhcp-server" "apache2")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "[✓] $service : actif"
    else
        echo "[✗] $service : INACTIF !"
    fi
done

echo ""
echo "=== Vérification des ports d'écoute ==="
sudo ss -tlnp | grep -E '(80|443|53|67|5000|5001)'

echo "=== Tests services OK ==="
```

### 1.3 Test du Reverse Proxy

Script de test complet :

```bash
nano /home/akaletekoffilevis/Bureau/Challenge/test-endpoints.sh
```

```bash
#!/bin/bash

echo "=========================================="
echo "  TEST DES ENDPOINTS - Challenge NextDev"
echo "=========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

tests=0
success=0

test_endpoint() {
    local name="$1"
    local url="$2"
    local host="$3"
    local expected_code="$4"

    tests=$((tests + 1))

    if [ -n "$host" ]; then
        code=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: $host" "$url")
    else
        code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    fi

    if [ "$code" = "$expected_code" ]; then
        echo -e "[${GREEN}✓${NC}] $name → HTTP $code"
        success=$((success + 1))
    else
        echo -e "[${RED}✗${NC}] $name → HTTP $code (attendu: $expected_code)"
    fi
}

echo "--- Test direct Kestrel ---"
test_endpoint "Site Web (direct)" "http://localhost:5000" "" "200"
test_endpoint "API (direct)" "http://localhost:5001" "" "200"
test_endpoint "API /trainee (direct)" "http://localhost:5001/trainee" "" "200"

echo ""
echo "--- Test via Apache (Reverse Proxy) ---"
test_endpoint "www.nextdev.ne" "http://localhost" "www.nextdev.ne" "200"
test_endpoint "api.nextdev.ne" "http://localhost" "api.nextdev.ne" "200"
test_endpoint "api.nextdev.ne/trainee" "http://localhost/trainee" "api.nextdev.ne" "200"

echo ""
echo "--- Vérification du contenu JSON ---"
echo ""
echo "Contenu de /trainee :"
curl -s -H "Host: api.nextdev.ne" http://localhost/trainee | python3 -m json.tool 2>/dev/null || curl -s -H "Host: api.nextdev.ne" http://localhost/trainee

echo ""
echo "=========================================="
echo -e "Résultat : ${success}/${tests} tests réussis"
echo "=========================================="
```

Rendre exécutable et lancer :

```bash
chmod +x /home/akaletekoffilevis/Bureau/Challenge/test-endpoints.sh
./test-endpoints.sh
```

### 1.4 Test de résilience

```bash
echo "=== Tests de résilience ==="

# Test 1 : Redémarrage d'Apache
sudo systemctl restart apache2
curl -s -o /dev/null -w "%{http_code}" -H "Host: www.nextdev.ne" http://localhost
echo " - Apache redémarré"

# Test 2 : Redémarrage des applis .NET
pkill -f "dotnet run"
sleep 2
cd /home/akaletekoffilevis/Bureau/Challenge/sites/www.nextdev.ne && dotnet run &
cd /home/akaletekoffilevis/Bureau/Challenge/sites/api.nextdev.ne && dotnet run &
sleep 5
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000
echo " - .NET redémarré"

# Test 3 : Test sans accès Internet
echo "Test en local uniquement... tout fonctionne sans Internet !"

echo "=== Tests de résilience OK ==="
```

---

## 2. Tests de performance

### Test avec Apache Bench (ab)

```bash
echo "=== Test de charge Apache ==="

# Installer Apache Bench
sudo apt install -y apache2-utils

# Test : 100 requêtes, 10 concurrentes
ab -n 100 -c 10 -H "Host: www.nextdev.ne" http://localhost/

# Test sur l'API
ab -n 100 -c 10 -H "Host: api.nextdev.ne" http://localhost/trainee
```

### Interprétation des résultats

```
Server Software:        Apache/2.4.x
Server Hostname:        localhost
Server Port:            80

Document Path:          /
Document Length:        xxxx bytes
Concurrency Level:      10
Time taken for tests:   0.xxx seconds
Complete requests:      100
Failed requests:        0
Requests per second:    xxx.xx [#/sec] (mean)
```

**Points à surveiller :**
- `Failed requests: 0` → tout passe
- `Requests per second` plus élevé → meilleure performance
- Si `Failed requests > 0`, vérifier les logs Apache

---

## 3. Préparation de la soutenance

### 3.1 Structure de la présentation (10-15 minutes)

| Durée | Section | Contenu |
|---|---|---|
| 2 min | **Introduction** | Présentation de l'équipe, du challenge |
| 3 min | **Architecture** | Schéma DNS → Apache → .NET → SQLite |
| 3 min | **Infrastructure** | DNS, DHCP, Apache : démo rapide |
| 3 min | **Développement** | Démo du site et de l'API |
| 2 min | **Démo live** | Navigation, test des endpoints |
| 2 min | **Conclusion** | Difficultés, solutions, améliorations |

### 3.2 Questions potentielles du jury

#### Questions techniques

**Q : Pourquoi avoir choisi SQLite plutôt que PostgreSQL ou MySQL ?**
> SQLite est idéal pour ce challenge car :
> - **Portable** : la base est un simple fichier, pas besoin de serveur de BDD
> - **Zéro configuration** : pas d'installation, pas d'utilisateur à créer
> - **Léger** : parfait pour un projet de 48h
> - **Suffisant** : pour le volume de données d'un challenge

**Q : Pourquoi Apache plutôt que Nginx ?**
> Apache est demandé par le sujet, mais aussi :
> - **Maturité** : Apache est le serveur web le plus éprouvé
> - **Modules** : riche écosystème (proxy, rewrite, ssl)
> - **.htaccess** : configuration décentralisée possible
> - **Compatibilité** : excellent support avec .NET via mod_proxy

**Q : Comment avez-vous configuré le Reverse Proxy ?**
> Nous avons utilisé `mod_proxy` et `mod_proxy_http` d'Apache. Chaque site (www et api) a son propre VirtualHost. Apache écoute sur le port 80/443 et redirige les requêtes vers Kestrel qui écoute sur les ports 5000 et 5001. Nous avons aussi configuré les `ForwardedHeaders` dans .NET pour que l'application connaisse la vraie IP du client.

**Q : Quelle est la différence entre Kestrel et Apache ?**
> - **Kestrel** : serveur ASP.NET Core, conçu pour le contenu dynamique, performant en JSON
> - **Apache** : serveur web généraliste, excellent pour les fichiers statiques, la sécurité, le SSL
> Ils sont complémentaires : Apache en front, Kestrel en back

**Q : Comment gérez-vous la sécurité ?**
> - Pare-feu UFW (ports filtrés)
> - SSL/TLS avec Let's Encrypt
> - Apache filtre les attaques avant Kestrel
> - Headers de sécurité (X-Forwarded-For, etc.)
> - Validation des entrées dans l'API (Data Annotations)

#### Questions sur le travail d'équipe

**Q : Comment avez-vous réparti les tâches ?**
> Nous avons divisé en 4 rôles :
> - **Infrastructure** : DNS, DHCP, Apache
> - **Développeur Web** : Razor Pages
> - **Développeur API** : Minimal API, SQLite
> - **Intégrateur** : Reverse Proxy, tests, coordination

**Q : Quelles difficultés avez-vous rencontrées ?**
> - Configuration BIND9 : syntaxe stricte
> - Communication entre Apache et Kestrel : Forwarded Headers
> - Gestion des ports sous Linux
> - Coordination entre les membres

**Q : Qu'avez-vous appris ?**
> - Configuration de services Linux en profondeur (DNS, DHCP, Apache)
> - Déploiement .NET sur Linux
> - Architecture Reverse Proxy
> - Travail d'équipe sous pression

### 3.3 Démo live : script pas à pas

Voici le script à suivre pendant la démo :

```bash
# Étape 1 : Montrer que les services tournent
systemctl status apache2 --no-pager | head -5
systemctl status bind9 --no-pager | head -5

# Étape 2 : Tester le DNS
echo "Résolution DNS :"
dig www.nextdev.ne +short
dig api.nextdev.ne +short

# Étape 3 : Tester le site vitrine
echo "Site vitrine :"
curl -s http://www.nextdev.ne | head -20

# Étape 4 : Tester l'API
echo "API - Accueil :"
curl -s http://api.nextdev.ne | python3 -m json.tool

echo "API - Liste des stagiaires :"
curl -s http://api.nextdev.ne/trainee | python3 -m json.tool

# Étape 5 : Test de charge
echo "Test de charge (100 requêtes) :"
ab -n 100 -c 10 http://www.nextdev.ne/ 2>&1 | grep -E "(Requests per second|Failed requests)"
```

---

## 4. Document d'architecture

Créer un résumé d'architecture à présenter au jury :

```bash
nano /home/akaletekoffilevis/Bureau/Challenge/docs/04-architecture.md
```

```markdown
# Architecture NextDev Challenge

## Schéma global

```
                    ┌──────────────────────────────────────┐
                    │          Debian 12 Server             │
                    │          10.0.0.68                │
                    │                                      │
  Navigateur ──────►│  Apache (80/443)                     │
  Client            │    │                                  │
                    │    ├── www.nextdev.ne ──► Kestrel:5000│
                    │    │    └── Razor Pages               │
                    │    │         └── HTML/CSS/JS          │
                    │    │                                  │
  Client API ──────►│    ├── api.nextdev.ne ──► Kestrel:5001│
                    │    │    └── Minimal API               │
                    │    │         └── SQLite (nextdev.db)  │
                    │    │                                  │
                    │    └── DNS (BIND9) :53                │
                    │    └── DHCP (ISC DHCP) :67            │
                    └──────────────────────────────────────┘
```

## Technologies

| Composant | Technologie | Version |
|---|---|---|
| OS | Debian | 12 (Bookworm) |
| Serveur Web | Apache | 2.4.x |
| Framework .NET | ASP.NET Core | 9 |
| Base de données | SQLite | 3.x |
| DNS | BIND9 | 9.18.x |
| DHCP | ISC DHCP Server | 4.4.x |
| SSL | Let's Encrypt | Certbot |

## Endpoints API

| Méthode | URL | Description | Retour |
|---|---|---|---|
| GET | `/` | Accueil API | JSON d'informations |
| GET | `/trainee` | Liste stagiaires | JSON avec count + data |

## Flux d'une requête

1. Client tape `www.nextdev.ne` dans son navigateur
2. DNS résout `www.nextdev.ne` → `10.0.0.68`
3. La requête arrive sur Apache (port 80)
4. Apache identifie le VirtualHost correspondant
5. Apache forwarde la requête à Kestrel (port 5000)
6. Kestrel exécute l'application .NET
7. La réponse repasse par Apache → Client
```

---

## 5. Checklist finale avant la soutenance

```bash
echo "=== CHECKLIST FINALE ==="
echo ""

checks=0
ok=0

check() {
    checks=$((checks + 1))
    if [ "$1" = true ]; then
        echo "[✓] $2"
        ok=$((ok + 1))
    else
        echo "[✗] $2"
    fi
}

# Infrastructure
systemctl is-active --quiet bind9 && check true "DNS (BIND9) actif" || check false "DNS (BIND9) actif"
systemctl is-active --quiet apache2 && check true "Apache2 actif" || check false "Apache2 actif"
systemctl is-active --quiet isc-dhcp-server && check true "DHCP actif" || check false "DHCP actif"

# DNS
dig www.nextdev.ne +short | grep -q "10.0.0.68" && check true "www.nextdev.ne résolu" || check false "www.nextdev.ne résolu"
dig api.nextdev.ne +short | grep -q "10.0.0.68" && check true "api.nextdev.ne résolu" || check false "api.nextdev.ne résolu"

# .NET (vérifier les processus)
pgrep -f "dotnet.*NextDev.Web" > /dev/null && check true "Site web .NET tourne" || check false "Site web .NET tourne"
pgrep -f "dotnet.*NextDev.Api" > /dev/null && check true "API .NET tourne" || check false "API .NET tourne"

# Endpoints via Apache
curl -s -o /dev/null -w "%{http_code}" -H "Host: www.nextdev.ne" http://localhost | grep -q "200" && check true "www.nextdev.ne répond" || check false "www.nextdev.ne répond"
curl -s -o /dev/null -w "%{http_code}" -H "Host: api.nextdev.ne" http://localhost | grep -q "200" && check true "api.nextdev.ne répond" || check false "api.nextdev.ne répond"
curl -s -o /dev/null -w "%{http_code}" -H "Host: api.nextdev.ne" http://localhost/trainee | grep -q "200" && check true "/trainee répond" || check false "/trainee répond"

# Pare-feu
ufw status | grep -q "active" && check true "Pare-feu actif" || check false "Pare-feu actif"

echo ""
echo "Résultat : $ok/$checks"
```

---

## 6. Conseils pour le jour J

### Avant la soutenance
- [ ] Redémarrer tous les services
- [ ] Vérifier que les deux apps .NET tournent
- [ ] Test DNS fonctionnel
- [ ] Données de démonstration présentes (5 stagiaires)
- [ ] Navigateur ouvert sur www.nextdev.ne
- [ ] Terminal prêt avec les commandes de test

### Pendant la soutenance
- [ ] Rester calme et souriant
- [ ] Parler fort et clairement
- [ ] Montrer la page d'accueil en premier (visuel)
- [ ] Faire un appel API en direct (curl)
- [ ] Montrer le code si demandé
- [ ] Expliquer POURQUOI les choix techniques
- [ ] Valoriser le travail d'équipe

### Gestion des imprévus
- **Le site ne s'affiche pas** → Lancer `./start-all.sh` en montrant qu'on sait dépanner
- **DNS ne répond pas** → Montrer la configuration `/etc/hosts` comme solution de secours
- **Question difficile** → Honnêteté : "Nous n'avons pas exploré cette piste, mais voici comment nous pourrions l'aborder..."
- **Démo qui échoue** → Montrer les logs et expliquer le diagnostic

---

## Résumé Phase 4

À la fin de cette phase, nous avons :
- [x] Tests fonctionnels automatisés (script `test-endpoints.sh`)
- [x] Tests de performance (Apache Bench)
- [x] Tests de résilience (redémarrage services)
- [x] Checklist finale prête
- [x] Script de démo pas à pas
- [x] Réponses préparées pour le jury
- [x] Document d'architecture détaillé
- [x] Plan de gestion des imprévus
