import boto3


def lambda_handler(event, context):
    # Get the service resource
    sqs = boto3.resource('sqs')

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName="lnkchk-pages")

    # Process messages by printing out body and optional author name
    for message in queue.receive_messages(MessageAttributeNames=["file", "line"]):
        # Get the custom author message attribute if it was set
        file_attribute = ""
        if message.message_attributes is not None:
            file_name = message.message_attributes.get("file").get("StringValue")
            if file_name:
                file_attribute = ' ({0})'.format(file_name)

        # Print out the body and author (if set)
        print('Hello, {0}!{1}'.format(message.body, file_attribute))

        # Let the queue know that the message is processed
        message.delete()



    