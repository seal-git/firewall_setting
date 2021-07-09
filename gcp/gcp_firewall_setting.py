"""
Google Cloud Platform で日本とアメリカからのアクセスだけを許可する
"""

import argparse
import subprocess
import ipaddress

CHUNK_SIZE = 256


def main():
    # IPアドレスを許可する国の一覧
    country_code_list = [
        'JP',
        'US',
    ]

    args = get_args()
    dry_run = args.dry_run

    addresses = get_addresses(country_code_list)

    create_rules(addresses, dry_run=dry_run)


def get_args():
    """コマンドライン引数を取得する"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='ドライラン')

    return parser.parse_args()


def create_rules(addresses, *, dry_run):
    """ファイヤウォールルールを複数件まとめて作成する"""
    for country, address_list in addresses.items():
        print(country, address_list)
        n = 0
        while True:
            start = n * CHUNK_SIZE
            stop = start + CHUNK_SIZE

            chunk_addresses = address_list[start:stop]
            if not chunk_addresses:
                break

            name = f'allow-{country.lower()}-{str(n).zfill(2)}'
            create_rule(name, chunk_addresses, dry_run=dry_run)
            n += 1


def check_address(addresses):
    # CIDRの有効性チェック
    # 有効なものだけをリストとして返す
    valid_addresses = []
    for address in addresses:
        try:
            ip = ipaddress.ip_network(address)
            valid_addresses.append(address)
        except:
            print(f'{address} id not valid')
    return valid_addresses


def create_rule(name, addresses, *, dry_run):
    """ファイヤウォールルールを 1 件作成する"""
    addresses = check_address(addresses)
    args = [
        'gcloud',
        'compute',
        'firewall-rules',
        'create',
        name,
        '--action=ALLOW',
        '--rules=tcp:80,tcp:443,icmp,tcp:22',
        '--direction=INGRESS',
        '--network=reskima',
        '--priority=10',
        '--no-enable-logging',
        '--source-ranges={}'.format(','.join(addresses)),
    ]
    if dry_run:
        print('Run:', ' '.join(args))
        return

    try:
        subprocess.run(args, check=True)
    except:
        pass
    return


def is_valid(line, country_code):
    if not line.startswith('#'):
        return True
    return False


def get_addresses(country_code_list):
    """アドレス一覧を取得する"""
    addresses = {}

    for country_code in country_code_list:
        lower_code = country_code.lower()
        args_ipv4 = [
            'curl',
            '-#',
            'http://ipverse.net/ipblocks/data/countries/' + lower_code + '.zone',
        ]
        filename = 'ipv4_cidr_' + lower_code + '.txt'
        with open(filename, 'w') as f:
            subprocess.run(args_ipv4, check=True, stdout=f)

        with open(filename, 'r') as f:
            addresses[country_code] = [l.strip()
                                       for l
                                       in f.readlines()
                                       if is_valid(l, country_code)]

    return addresses


if __name__ == '__main__':
    main()
