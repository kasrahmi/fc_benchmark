#include <iostream>
#include <string>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

#include "absl/flags/flag.h"
#include "absl/flags/parse.h"

ABSL_FLAG(std::string, addr, "192.168.0.2", "Server address");
ABSL_FLAG(int, port, 50051, "Server port");

void RunClient(const std::string& ip, int port, const std::string& message) {
  int sock = 0;
  struct sockaddr_in serv_addr;

  if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    std::cout << "Socket creation error" << std::endl;
    return;
  }

  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(port);

  if (inet_pton(AF_INET, ip.c_str(), &serv_addr.sin_addr) <= 0) {
    std::cout << "Invalid address / Address not supported" << std::endl;
    return;
  }

  if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
    std::cout << "Connection failed" << std::endl;
    return;
  }

  send(sock, message.c_str(), message.size(), 0);
  char buffer[1024] = {0};
  read(sock, buffer, 1024);
  std::cout << "Client received: " << buffer << std::endl;

  close(sock);
}

int main(int argc, char** argv) {
  absl::ParseCommandLine(argc, argv);
  std::string addr = absl::GetFlag(FLAGS_addr);
  int port = absl::GetFlag(FLAGS_port);
  std::string user("world");
  RunClient(addr, port, user);
  return 0;
}