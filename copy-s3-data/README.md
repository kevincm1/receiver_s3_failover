# ReceiverFailoverNotification
This lambda is meant to be triggered by an S3 notification for receivers.

It writes to a given SNS topic the S3 location for the object which triggered this notification. It only publishes to SNS if the receiver object contains data any of the specified receivers (by setting `PROVIDERS_TO_PROCESS`).