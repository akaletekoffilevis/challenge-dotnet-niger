# Phase 1 : Infrastructure (H0 - H12)

---

## 1. Installation du système d'exploitation

### Choix de l'OS : Debian 12 (Bookworm)

Nous avons choisi **Ubuntu 26.04 LTS** pour sa stabilité, sa compatibilité avec .NET 9 et sa facilité d'utilisation. Ubuntu est le choix idéal pour un serveur de production.

### Étapes d'installation

#### Téléchargement et installation
1. Télécharger Ubuntu 26.04 LTS depuis [ubuntu.com](https://www.ubuntu.com)
2. Créer une clé USB bootable avec `dd` ou `Rufus`
3. Installer Ubuntu avec les options minimales (pas d'environnement de bureau)

#### Configuration réseau statique
Après l'installation, configurer une IP statique :

```bash
# Éditer le fichier Netplan
sudo nano /etc/network/interfaces
```

Contenu :

```bash
# Interface loopback
auto lo
iface lo inet loopback

# Interface réseau principale
auto eth0
iface eth0 inet static
     address 10.0.0.68
    netmask 255.255.0.0
    gateway 10.0.0.1
    dns-nameservers 8.8.8.8 1.1.1.1
```

Redémarrer le réseau :

```bash
sudo systemctl restart networking
```

#### Mise à jour des paquets

```bash
sudo apt update && sudo apt upgrade -y
```

#### Installation des outils de base

```bash
sudo apt install -y curl wget git nano ufw htop net-tools dnsutils
```

---

## 2. Configuration DNS (BIND9)

### Rôle du DNS
Le DNS (Domain Name System) permet de résoudre les noms de domaine (`www.nextdev.ne`, `api.nextdev.ne`) en adresses IP. Sans DNS, les navigateurs ne sauraient pas où trouver nos serveurs.

### Installation de BIND9

```bash
sudo apt install -y bind9 bind9utils bind9-doc
```

### Configuration de la zone `nextdev.ne`

Éditer le fichier de configuration des zones nommées :

```bash
sudo nano /etc/bind/named.conf.local
```

Ajouter :

```bind
zone "nextdev.ne" {
    type master;
    file "/etc/bind/db.nextdev.ne";
    allow-query { any; };
};
```

### Création du fichier de zone

```bash
sudo nano /etc/bind/db.nextdev.ne
```

Contenu :

```bind
; Zone DNS pour nextdev.ne
$TTL    604800
@       IN      SOA     ns1.nextdev.ne. admin.nextdev.ne. (
                    2024010101   ; Serial
                    604800       ; Refresh
                    86400        ; Retry
                    2419200      ; Expire
                    604800       ; Negative Cache TTL
)

; Name Servers
@       IN      NS      ns1.nextdev.ne.
@       IN      A       10.0.0.68

; Enregistrements A (IPv4)
ns1     IN      A       10.0.0.68
www     IN      A       10.0.0.68
api     IN      A       10.0.0.68

; Enregistrement CNAME (alias)
@       IN      CNAME   www.nextdev.ne.
```

### Explication des enregistrements

| Enregistrement | Nom | Valeur | Explication |
|---|---|---|---|
| SOA | nextdev.ne | ns1.nextdev.ne | Start of Authority : définit le serveur DNS principal |
| NS | nextdev.ne | ns1.nextdev.ne | Name Server : déclare notre serveur comme autoritaire |
| A | www.nextdev.ne | 10.0.0.68 | Associe le sous-domaine www à l'IP du serveur |
| A | api.nextdev.ne | 10.0.0.68 | Associe le sous-domaine api à l'IP du serveur |
| CNAME | nextdev.ne | www.nextdev.ne | Redirection du domaine nu vers www |

### Vérification de la syntaxe et redémarrage

```bash
# Vérifier la syntaxe
sudo named-checkconf

# Vérifier la zone
sudo named-checkzone nextdev.ne /etc/bind/db.nextdev.ne

# Redémarrer BIND9
sudo systemctl restart bind9

# Activer au démarrage
sudo systemctl enable bind9

# Vérifier le statut
sudo systemctl status bind9
```

### Test de résolution DNS

```bash
# Depuis le serveur
dig www.nextdev.ne @localhost

# Résultat attendu :
# ;; ANSWER SECTION:
# www.nextdev.ne. 60400 IN A 10.0.0.68

# Tester l'API
dig api.nextdev.ne @localhost

# Avec nslookup
nslookup www.nextdev.ne localhost
```

---

## 3. Configuration DHCP (ISC DHCP Server)

### Rôle du DHCP
Le DHCP (Dynamic Host Configuration Protocol) attribue automatiquement des adresses IP aux machines du réseau. Cela évite d'avoir à configurer manuellement chaque poste client.

### Installation

```bash
sudo apt install -y isc-dhcp-server
```

### Configuration

Éditer le fichier de configuration :

```bash
sudo nano /etc/dhcp/dhcpd.conf
```

Contenu :

```dhcp
# Configuration du serveur DHCP

# Domaine et serveurs DNS
option domain-name "nextdev.ne";
option domain-name-servers 10.0.0.68, 8.8.8.8;

# Temps de bail par défaut (en secondes)
default-lease-time 600;
max-lease-time 7200;

# Le serveur est autoritaire pour ce réseau
authoritative;

# Définition du sous-réseau
subnet 10.0.0.0 netmask 255.255.0.0 {
    range 10.0.0.50 10.0.0.200;          # Plage d'adresses attribuables
    option routers 10.0.0.1;             # Passerelle par défaut
    option broadcast-address 10.0.255.255; # Adresse de broadcast
    option domain-name-servers 10.0.0.68, 8.8.8.8;
}
```

### Spécifier l'interface d'écoute

```bash
sudo nano /etc/default/isc-dhcp-server
```

Modifier :

```bash
INTERFACESv4="eth0"
INTERFACESv6=""
```

### Démarrage du service

```bash
sudo systemctl restart isc-dhcp-server
sudo systemctl enable isc-dhcp-server
sudo systemctl status isc-dhcp-server
```

### Test du DHCP

```bash
# Voir les baux attribués
sudo dhcp-lease-list

# Ou consulter le fichier des baux
sudo cat /var/lib/dhcp/dhcpd.leases
```

---

## 4. Installation et Configuration d'Apache2

### Rôle d'Apache2
Apache2 est le serveur web qui va agir comme **Reverse Proxy**. Il reçoit les requêtes HTTP des clients et les redirige vers les applications .NET (Kestrel). Cela apporte :
- **Sécurité** : Apache gère les attaques avant d'atteindre .NET
- **SSL/TLS** : Apache gère le chiffrement HTTPS
- **Performance** : Apache sert les fichiers statiques plus rapidement

### Installation

```bash
sudo apt install -y apache2 apache2-utils
```

### Activation des modules nécessaires

```bash
# Proxy : pour rediriger les requêtes vers .NET
sudo a2enmod proxy
sudo a2enmod proxy_http

# Réécriture d'URL
sudo a2enmod rewrite

# SSL pour le chiffrement
sudo a2enmod ssl

# En-têtes HTTP
sudo a2enmod headers

# Redémarrer Apache
sudo systemctl restart apache2
```

### Explication des modules

| Module | Utilité |
|---|---|
| `proxy` | Active le système de proxy dans Apache |
| `proxy_http` | Permet le proxy HTTP (vers Kestrel) |
| `rewrite` | Réécriture d'URL (redirections) |
| `ssl` | Support HTTPS (chiffrement SSL/TLS) |
| `headers` | Manipulation des en-têtes HTTP |

### Création des VirtualHosts

Les VirtualHosts permettent à Apache de servir plusieurs sites web sur la même machine.

#### VirtualHost pour `www.nextdev.ne`

```bash
sudo nano /etc/apache2/sites-available/www.nextdev.ne.conf
```

```apache
<VirtualHost *:80>
    ServerName www.nextdev.ne
    ServerAlias nextdev.ne

    # Journalisation
    ErrorLog ${APACHE_LOG_DIR}/www.nextdev.ne_error.log
    CustomLog ${APACHE_LOG_DIR}/www.nextdev.ne_access.log combined

    # Proxy vers Kestrel (.NET Razor Pages)
    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/

    # En-têtes pour le forwarding
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port "80"
</VirtualHost>
```

#### VirtualHost pour `api.nextdev.ne`

```bash
sudo nano /etc/apache2/sites-available/api.nextdev.ne.conf
```

```apache
<VirtualHost *:80>
    ServerName api.nextdev.ne

    # Journalisation
    ErrorLog ${APACHE_LOG_DIR}/api.nextdev.ne_error.log
    CustomLog ${APACHE_LOG_DIR}/api.nextdev.ne_access.log combined

    # Proxy vers Kestrel (.NET Minimal API)
    ProxyPreserveHost On
    ProxyPass / http://localhost:5001/
    ProxyPassReverse / http://localhost:5001/

    # En-têtes pour le forwarding
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port "80"
</VirtualHost>
```

### Activation des sites

```bash
sudo a2ensite www.nextdev.ne.conf
sudo a2ensite api.nextdev.ne.conf

# Désactiver le site par défaut
sudo a2dissite 000-default.conf

# Recharger Apache
sudo systemctl reload apache2
```

---

## 5. Configuration du Pare-Feu (UFW)

### Rôle du pare-feu
UFW (Uncomplicated Firewall) est un pare-feu qui protège notre serveur en ne laissant passer que les ports autorisés.

```bash
# Activer UFW
sudo ufw enable

# SSH (port 22)
sudo ufw allow 22/tcp

# HTTP (port 80)
sudo ufw allow 80/tcp

# HTTPS (port 443)
sudo ufw allow 443/tcp

# DNS (port 53)
sudo ufw allow 53/tcp
sudo ufw allow 53/udp

# DHCP (port 67)
sudo ufw allow 67/udp

# Vérifier les règles
sudo ufw status verbose
```

### Résultat attendu

```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
53/tcp                     ALLOW IN    Anywhere
53/udp                     ALLOW IN    Anywhere
67/udp                     ALLOW IN    Anywhere
```

---

## 6. Tests de vérification (Phase 1)

### Vérification des services

```bash
# Vérifier que tous les services tournent
systemctl status bind9
systemctl status isc-dhcp-server
systemctl status apache2
```

### Test DNS

```bash
# Depuis n'importe quelle machine du réseau
nslookup www.nextdev.ne 10.0.0.68
nslookup api.nextdev.ne 10.0.0.68
```

### Test DHCP

```bash
# Sur une machine cliente configurée en DHCP
ip addr show
# Vérifier que l'IP reçue est dans la plage 10.0.0.50-200
```

### Test Apache

```bash
# Pour l'instant, les sites renvoient une erreur 503
# (car .NET n'est pas encore installé)
curl -H "Host: www.nextdev.ne" http://localhost
curl -H "Host: api.nextdev.ne" http://localhost
```

---

## Résumé Phase 1

À la fin de cette phase, nous avons :
- [x] Un serveur Ubuntu 26.04 LTS avec IP statique
- [x] Un serveur DNS (BIND9) qui résout `www.nextdev.ne` et `api.nextdev.ne`
- [x] Un serveur DHCP (ISC DHCP) qui attribue des IPs dans la plage 10.0.0.50-200
- [x] Un serveur Apache2 avec modules proxy activés
- [x] Deux VirtualHosts prêts à proxyer vers .NET
- [x] Un pare-feu UFW qui protège le serveur
