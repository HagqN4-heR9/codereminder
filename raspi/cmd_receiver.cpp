//cmd_receiver.cpp  (Raspberry Pi)
// PC側からの入力コマンドを受信し、std::stringとしてパースして実行する
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstdint>
#include <string>
#include <iostream>
#include <stdexcept>

const char* LISTEN_IP = "0.0.0.0";
const int   CMD_PORT  = 9997;

// ちょうどnバイト受信する
bool recv_exact(int sock, uint8_t* buf, size_t n) {
    size_t got = 0;
    while (got < n) {
        ssize_t r = recv(sock, buf + got, n - got, 0);
        if (r <= 0) return false;
        got += static_cast<size_t>(r);
    }
    return true;
}

// 受信したコマンド文字列を処理する
void handle_command(const std::string& cmd) {
    std::cout << "[CMD] 受信: " << cmd << std::endl;

    if      (cmd == "LED_ON")  { /* GPIO LED点灯処理 */ }
    else if (cmd == "LED_OFF") { /* GPIO LED消灯処理 */ }
    else if (cmd.rfind("MSG:", 0) == 0) {
        std::string msg = cmd.substr(4);
        std::cout << "[MSG] " << msg << std::endl;
    }
    else { std::cout << "[CMD] 不明: " << cmd << std::endl; }
}

int main(){
    int srv = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port   = htons(CMD_PORT);
    inet_pton(AF_INET, LISTEN_IP, &addr.sin_addr);

    bind(srv, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    listen(srv, 1);
    std::cout << "[CMD_SERVER] port " << CMD_PORT << " 待受中\n";

    sockaddr_in cli{};
    socklen_t cli_len = sizeof(cli);
    int conn = accept(srv, reinterpret_cast<sockaddr*>(&cli), &cli_len);
    std::cout << "[CMD_SERVER] PC接続完了\n";

    while (true) {
       // ① 4バイトのサイズヘッダを受信
        uint32_t net_size = 0;
        if (!recv_exact(conn, reinterpret_cast<uint8_t*>(&net_size), 4)) break;
        uint32_t size = ntohl(net_size);   // ネットワーク→ホストバイトオーダー

        // ② コマンド本体を受信してstd::stringに変換
        std::string cmd(size, '\0');
        if (!recv_exact(conn, reinterpret_cast<uint8_t*>(cmd.data()), size)) break;

        handle_command(cmd);
    }
    close(conn);
    close(srv);
    return 0;
}