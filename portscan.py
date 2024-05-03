import socket, argparse, threading

g_banners: [{int: bytes}] = []
g_port_results: [{int: bool}] = []
g_max_threads = 100


def tcp_scan(target: str, port: int):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.settimeout(1)
        result = s.connect_ex((target, int(port)))

        if result == 0:
            
            g_port_results.append({port: True})
            try:
                s.send(b'GET / HTTP/1.0\r\n\r\n')
                banner = s.recv(1024)
                g_banners.append({port: banner})
            except Exception as e:
                g_banners.append({port: "none".encode()})
        else:
            g_port_results.append({port: False})
        s.close()

    except socket.error as e:
        print(f"Error: {e}")


def threaded_scan(target_ip: str, ports: list[int]):
    threads = []
    for port in ports:
        t = threading.Thread(target=tcp_scan, args=(target_ip, port))
        threads.append(t)

        if len(threads) >= g_max_threads:
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            threads = []

    for t in threads:
        t.start()
    for t in threads:
        t.join()


def print_result():
    for result in g_port_results:
        for port in result:
            if result[port] == True:
                print(f"[+] Port: {port} is Open!")
                for banner in g_banners:
                    if port == list(banner.keys())[0]:
                        if banner[port].decode() != "none":
                            print(f"[*] Port: {port}, Banner: \n{banner[port].decode().split("\r\n\r\n")[0]}\n")

def main():
    parser = argparse.ArgumentParser(usage="python3 portscan.py <target> <port/s> # use 80,8080,443 to threaded_scan multiple ports")
    parser.add_argument("target", help="Target IP address")
    parser.add_argument("ports", help="Port that gets Scanned. Use comma seperated ports to threaded_scan multiple ports")
    args = parser.parse_args()

    if '-' in args.ports:
        port_range = args.ports.split("-")
        ports = [ port for port in range(int(port_range[0]), int(port_range[1]) + 1)]
        threaded_scan(args.target, ports)
    else:
        ports = args.ports.split(",")
        threaded_scan(args.target, ports)

    print_result()
    

if __name__ == "__main__":    
    main()
