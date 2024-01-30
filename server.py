from concurrent import futures
import grpc
import time
import json

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc


class ChatServer(rpc.ChatServerServicer):
    def __init__(self):
        self.chats = []
        self.chat_data = []

    def ChatStream(self, request_iterator, context):
        last_index = 0
        while True:
            while len(self.chats) > last_index:
                n = self.chats[last_index]
                last_index += 1
                yield n

    def SendNote(self, request: chat.Note, context):
        print("[{}] {}: {}: {}".format(request.name, request.id, request.title, request.content))
        self.chats.append(request)

        chat_entry = {
            "name": request.name,
            "module_id": request.id,
            "subsection_id": request.title,
            "content": request.content,
            "timestamp": str(int(time.time())),
        }
        self.chat_data.append(chat_entry)

        with open("chat_data.json", "w") as json_file:
            json.dump(self.chat_data, json_file)

        return chat.Empty()


if __name__ == '__main__':
    port = 11912
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    while True:
        time.sleep(64 * 64 * 100)
