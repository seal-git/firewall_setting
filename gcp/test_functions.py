from gcp_firewall_setting import *

addresses = get_addresses(['JP', 'US'])
print(addresses)
print(addresses['JP'][0])

create_rule('JP', addresses['JP'][0:10], dry_run=True)

create_rules(addresses, dry_run=True)