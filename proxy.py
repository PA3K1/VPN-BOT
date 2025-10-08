PROXIES = [
    {"scheme": "http", "hostname": "138.199.48.1", "port": 8080},
    {"scheme": "http", "hostname": "193.122.107.45", "port": 3128},
    {"scheme": "http", "hostname": "194.113.233.130", "port": 3128},
    {"scheme": "http", "hostname": "51.158.68.133", "port": 8811},
    {"scheme": "http", "hostname": "191.101.39.27", "port": 8080},
]

def get_proxy():
    import random
    return random.choice(PROXIES)