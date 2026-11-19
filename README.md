# TP7 - OPNsense : Provisioning Zero-Touch

Scenario simule : un nouvel OPNsense est configure entierement par script Python, sans passer par l'interface web.

## Ce que fait le script

`zero_touch_provision.py` configure via l'API REST native d'OPNsense :

1. **DHCP (Kea DHCPv4)** : activation sur l'interface LAN, creation du subnet `192.168.56.0/24` avec pool `192.168.56.150-192.168.56.200`, passerelle et DNS, puis `reconfigure`.
2. **NAT (port forward)** : redirection TCP du port 8080 vers `192.168.56.10:8080`, puis application avec `filter/apply`.

Le script est **idempotent** : il verifie l'existant avant de creer (`[SKIP]` si deja present) et peut etre relance sans doublon. Les erreurs HTTP sont gerees.

## Installation

    python -m venv venv
    venv\Scripts\Activate.ps1
    pip install requests python-dotenv

## Configuration

Generer une cle API (System > Access > Users > root), puis creer un fichier `.env` (exclu du depot par `.gitignore`) :

    OPNSENSE_HOST=192.168.56.101
    OPNSENSE_KEY=votre_cle
    OPNSENSE_SECRET=votre_secret

Les parametres du scenario (plage DHCP, DNS, regle NAT) sont dans le dictionnaire `CONFIG` en haut de `zero_touch_provision.py`.

## Lancement

    python zero_touch_provision.py

## Scripts

- `test_status.py` : premier appel authentifie
- `discover.py`, `show_kea.py`, `show_interfaces.py` : decouverte des endpoints et de la configuration
- `dhcp_config.py` : configuration DHCP seule
- `nat_config.py` : regle NAT seule
- `nat_cleanup.py` : suppression des doublons de la regle NAT
- `zero_touch_provision.py` : scenario complet (DHCP + NAT)

## Notes

- OPNsense recent utilise **Kea** pour le DHCP : endpoints `/kea/dhcpv4/...`.
- Un changement n'est actif qu'apres l'appel d'application (`/kea/service/reconfigure`, `/firewall/filter/apply`).
- La cle et le secret API ne sont jamais commites.
