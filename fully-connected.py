import tensorflow as tf
import numpy as np
import os as os

tf.logging.set_verbosity(tf.logging.INFO)
def weight_init(shape):
    initial = tf.truncated_normal(shape, stddev=0.01)
    return tf.Variable(initial);

def bias_init(shape):
    initial = tf.constant(0.1, shape= shape)
    return tf.Variable(initial)


def custom_model_fn(features, labels, mode):
    """Model function for PA1"""

    # Write your custom layer
    # Input Layer
    #input_layer = tf.reshape(features["x"], [-1, 28, 28, 1]) # You also can use 1 x 784 vector

    # Implemented by Jihoon #
    input_layer = tf.reshape(features["x"], [-1, 784])
    # Layer 1
    w_fc1 = weight_init([784, 784])
    b_fc1 = bias_init([784])
    h_fc1 = tf.nn.leaky_relu(tf.matmul(input_layer, w_fc1) + b_fc1) # Using LeakyReLU

    # Layer 2
    w_fc2 = weight_init([784,784])
    b_fc2 = bias_init([784])
    h_fc2 = tf.nn.leaky_relu(tf.matmul(h_fc1, w_fc2) + b_fc2)

    # Layer 3
    w_fc3 = weight_init([784,784])
    b_fc3 = bias_init([784])
    h_fc3 = tf.nn.leaky_relu(tf.matmul(h_fc2, w_fc3) + b_fc3)

    # Layer 4
    w_fc4 = weight_init([784,784])
    b_fc4 = bias_init([784])
    h_fc4 = tf.nn.leaky_relu(tf.matmul(h_fc3, w_fc4) + b_fc4)

    
    # Layer 5
    w_fc5 = weight_init([784, 1024])
    b_fc5 = bias_init([1024])
    h_fc5 = tf.nn.leaky_relu(tf.matmul(h_fc4, w_fc5) + b_fc5)

    # Layer 6
    w_fc6 = weight_init([1024, 1024])
    b_fc6 = bias_init([1024])
    h_fc6 = tf.nn.leaky_relu(tf.matmul(h_fc5, w_fc6) + b_fc6)

    # Output logits Layer , the last layer
    logits = tf.layers.dense(inputs=h_fc6, units=10)

    predictions = {
      # Generate predictions (for PREDICT and EVAL mode)
      "classes": tf.argmax(input=logits, axis=1),
      # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
      # `logging_hook`.
      "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }

    # In predictions, return the prediction value, do not modify
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # Select your loss and optimizer from tensorflow API
    # Calculate Loss (for both TRAIN and EVAL modes)
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits= logits) # Refer to tf.losses

    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdamOptimizer(learning_rate=0.001) # Refer to tf.train, Using AdamOptimizer
        train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {"accuracy": tf.metrics.accuracy(labels=labels, predictions=predictions["classes"])}
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


if __name__ == '__main__':
    # Write your dataset path
    #dataset_train = np.load('train_data')
    #dataset_eval =  np.load('valid_data')
    #test_data =  np.load('test_data')
    #dataset_train = np.load('train')
    #dataset_eval = np.load('valid')
    #test_data = np.load('test')

    dataset_train = open(os.path.expanduser('train.npy'))
    dataset_train = np.load(dataset_train)

    dataset_eval = open(os.path.expanduser('valid.npy'))
    dataset_eval = np.load(dataset_eval)

    test_data = open(os.path.expanduser('test.npy'))
    test_data = np.load(test_data)

    train_data = dataset_train[:,:784]
    train_labels = dataset_train[:,784].astype(np.int32)
    eval_data = dataset_eval[:,:784]
    eval_labels = dataset_eval[:,784].astype(np.int32)

    # Save model and checkpoint
    classifier = tf.estimator.Estimator(model_fn=custom_model_fn, model_dir="./model")

    # Set up logging for predictions
    tensors_to_log = {"probabilities": "softmax_tensor"}
    logging_hook = tf.train.LoggingTensorHook(tensors=tensors_to_log, every_n_iter=50)

    # Train the model. You can train your model with specific batch size and epoches
    train_input = tf.estimator.inputs.numpy_input_fn(x={"x": train_data}, y=train_labels, batch_size=100, num_epochs=None, shuffle=True)
    classifier.train(input_fn=train_input, steps=20000, hooks=[logging_hook])

    # Eval the model. You can evaluate your trained model with validation data
    eval_input = tf.estimator.inputs.numpy_input_fn(x={"x": eval_data}, y=eval_labels, num_epochs=1, shuffle=False)
    eval_results = classifier.evaluate(input_fn=eval_input)

    ## ----------- Do not modify!!! ------------ ##
    # Predict the test dataset
    pred_input = tf.estimator.inputs.numpy_input_fn(x={"x": test_data}, shuffle=False)
    pred_results = classifier.predict(input_fn=pred_input)
    result = np.asarray([x.values()[1] for x in list(pred_results)])
    ## ----------------------------------------- ##
    np.save('20150441_network_7.npy', result)
