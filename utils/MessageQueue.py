class MessageQueue:
    def __init__(self, size: int):
        self.size = size
        self.buffer = {}
        self.order = []
        self.head = 0
        self.tail = 0
        self.count = 0

    def add_message(self, message_id: str, _message: str) -> str:
        if message_id in self.buffer:
            # if Message ID exists, update the message
            self.buffer[message_id] = _message
        else:
            # if Message ID does not exist, add the message
            if self.count < self.size:
                self.count += 1
            else:
                # if the buffer is full, remove the oldest message
                oldest_id = self.order[self.head]
                del self.buffer[oldest_id]
                self.head = (self.head + 1) % self.size

            self.buffer[message_id] = _message
            if self.count <= self.size:
                self.order.append(message_id)
            else:
                self.order[self.tail] = message_id
            self.tail = (self.tail + 1) % self.size

        return message_id

    def get_message(self, message_id: str):
        return self.buffer.get(message_id)

    def update_message(self, message_id: str, new_message: str):
        if message_id in self.buffer:
            self.buffer[message_id] = new_message
            return True
        return False

    def get_all_messages(self):
        messages = []
        index = self.head
        for _ in range(self.count):
            message_id = self.order[index]
            if message_id in self.buffer:
                messages.append((message_id, self.buffer[message_id]))
            index = (index + 1) % self.size
        return messages


class MessageQueueManager:
    def __init__(self):
        self.queues = {}
        self.next_id = 0

    def create_queue(self, size):
        queue_id = self.next_id
        self.queues[queue_id] = MessageQueue(size)
        self.next_id += 1
        return queue_id

    def get_queue(self, queue_id):
        return self.queues.get(queue_id)

    def delete_queue(self, queue_id):
        if queue_id in self.queues:
            del self.queues[queue_id]
            return True
        return False


if __name__ == '__main__':
    # 示例使用
    mq_manager = MessageQueueManager()

    # 创建两个消息队列
    queue_id1 = mq_manager.create_queue(20)
    queue_id2 = mq_manager.create_queue(20)

    # 获取并使用消息队列
    mq1 = mq_manager.get_queue(queue_id1)
    mq2 = mq_manager.get_queue(queue_id2)

    # 添加消息到第一个队列
    for i in range(22):
        if i == 7:
            mq1.add_message(f"5群 q: {i}", f"占位符{i}")
            continue
        if i == 14:
            mq1.add_message(f"5群 q: {i}", f"占位符{i}")
            continue
        mq1.add_message(f"5群 q: {i}", f"Message {i}")

    # 读取消息
    print("第1个消息, 已被后续的消息替代 显示None:", mq1.get_message("5群 q: 1"))

    print("\n假设第1个是图片\n因为群内高并发消息导致被删除 同时图片请求完成 尝试替代占位符获取的返回值: ",
          mq1.get_message("5群 q: 1"), end='\n\n')

    print("第7个消息 图片占位符消息: ", mq1.get_message("5群 q: 7"))
    print("第13个消息", mq1.get_message("5群 q: 13"))

    # 更新消息
    mq1.update_message("5群 q: 7", "图片标题7")
    print("假设图片请求完成 替代占位符后:", mq1.get_message("5群 q: 7"))

    print('-' * 20)
    # 读取所有消息
    print("读取所有消息 模拟假人触发随机发送")
    all_messages = mq1.get_all_messages()
    for message in all_messages:
        print(message)

    # 删除第二个队列
    mq_manager.delete_queue(queue_id2)
