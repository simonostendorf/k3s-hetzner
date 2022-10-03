import argparse
from hcloud import Client

def find_used_ips(network, ip_begin):
    max_ip = 0
    for srv in network.data_model.servers:
        server_id = srv.data_model.id
        server_obj = client.servers.get_by_id(server_id)
        private_net = server_obj.data_model.private_net[0]
        
        if private_net.ip.startswith(ip_begin):
            curr_ip = int(private_net.ip.split('.')[3])
            if curr_ip > max_ip:
                max_ip = curr_ip
    return max_ip

def attach_to_network(nw, ip, srv, retrys=0):
    if retrys >= 5:
        print("Failed to attach server to network. Max retrys reached. Exiting.")
        return

    try:
        srv.attach_to_network(network=nw, ip=ip)
    except Exception as ex:
        if ex.message == 'server already attached':
            print('server already in network. skipping')
        elif ex.message == 'ip already in use':
            print('ip already in use. try again with next ip (retry: ' + str(retrys) + ')')
            next_ip = ip.split('.')[0] + '.' + ip.split('.')[1] + '.' + ip.split('.')[2] + '.' + str(int(ip.split('.')[3]) + 1)
            attach_to_network(nw, next_ip, srv, retrys+1)
        elif ex.message == 'provided IP is not available':
            print('ip not available. try again with next ip (retry: ' + str(retrys) + ')')
            next_ip = ip.split('.')[0] + '.' + ip.split('.')[1] + '.' + ip.split('.')[2] + '.' + str(int(ip.split('.')[3]) + 1)
            attach_to_network(nw, next_ip, srv, retrys+1)
        else:
            print('unknown error. try again (retry: ' + str(retrys) + ')')
            print(ex.message)
            attach_to_network(nw, ip, srv, retrys+1)

parser = argparse.ArgumentParser()

parser.add_argument('--token', help='Hetzner Cloud API Token', required=True)
parser.add_argument('--server_name', help='Server Name', required=True)
parser.add_argument('--network_id', help='Private Network ID', required=True)

args = parser.parse_args()

client = Client(token=args.token)

server = client.servers.get_by_name(args.server_name)

network = client.networks.get_by_id(args.network_id)

if server.data_model.datacenter.location.name == "hel1":
    max_ip = find_used_ips(network, "10.2.0.")
    attach_to_network(network, "10.2.0." + str(max_ip + 1), server)
elif server.data_model.datacenter.location.name == "fsn1":
    max_ip = find_used_ips(network, "10.2.1.")
    attach_to_network(network, "10.2.1." + str(max_ip + 1), server)
elif server.data_model.datacenter.location.name == "nbg1":
    max_ip = find_used_ips(network, "10.2.2.")
    attach_to_network(network, "10.2.2." + str(max_ip + 1), server)
