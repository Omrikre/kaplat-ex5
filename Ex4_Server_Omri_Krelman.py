from flask import Flask, request, jsonify
import math
import logging
import os
import sys
import shutil
import time

app = Flask(__name__)
host = "localhost"
port = 9583
stack = list()
simple_sign = ["plus", "minus", "times", "divide", "pow"]
one_num_sign = ["abs", "fact"]
requestNum = 0


@app.route('/stack/size', methods=['GET'])
def get_stack_size():
    startTime = requestLogger("GET", "/stack/size")
    logging.getLogger("stack-logger").info("Stack size is " + str(len(stack)) + " | request #%d", requestNum)
    revStack = list(reversed(stack))
    logging.getLogger("stack-logger").debug("Stack content (first == top): " + str(revStack) + " | request #%d", requestNum)
    requestLoggerEnd(startTime)
    response = jsonify({"result": str(len(stack))})
    return response, 200

@app.route('/stack/operate', methods=['GET'])
def invoke_operation():
    startTime = requestLogger("GET", "/stack/operate")
    stackLogger = logging.getLogger('stack-logger')

    sign = request.args.get('operation').lower()
    if sign in simple_sign:
        if len(stack) < 2:
            stackLogger.error("Server encountered an error ! message: Error: cannot implement operation " + sign + ". It requires 2 arguments and the stack has only " + str(len(stack)) + " arguments | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error: cannot implement operation" + sign + ". It requires 2 arguments and the stack has only " + str(len(stack)) + " arguments"})
            return response, 409
        numbers = [stack.pop(), stack.pop()]
        if numbers[1] == 0 and sign == "divide":
            stackLogger.error("Server encountered an error ! message: Error while performing operation Divide: division by 0 | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error while performing operation Divide: division by 0"})
            return response, 409
        else:
            result = str(calc(sign, numbers))
            stackLogger.info("Performing operation %s. Result is %s | stack size: %d | request #%d", sign, result, len(stack), requestNum)
            stackLogger.debug("Performing operation: %s(%s) = %s | request #%d", sign, str(numbers).replace('[','').replace(']','').replace(' ',''), result, requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"result": result})
            return response, 200

    elif sign in one_num_sign:
        if len(stack) < 1:
            stackLogger.error("Server encountered an error ! message: Error: cannot implement operation " + sign + ". It requires 1 arguments and the stack has only" + str(len(stack)) + "arguments | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error: cannot implement operation" + sign + ". It requires 1 arguments and the stack has only" + str(len(stack)) + "arguments"})
            return response, 409
        numbers = [stack.pop()]
        if numbers[0] < 0 and sign == "fact":
            stackLogger.error("Server encountered an error ! message: Error while performing operation Factorial: not supported for the negative number | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error while performing operation Factorial: not supported for the negative number"})
            return response, 409
        else:
            result = str(calc(sign, numbers))
            stackLogger.info("Performing operation %s. Result is %s | stack size: %d | request #%d", sign, result, len(stack), requestNum)
            stackLogger.debug("Performing operation: %s(%s) = %s | request #%d", sign, str(numbers).replace('[','').replace(']','').replace(' ',''), result, requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"result": result})
            return response, 200
    else:
        stackLogger.error("Server encountered an error ! message: Error: unknown operation: " + sign + " | request #%d", requestNum)
        requestLoggerEnd(startTime)
        response = jsonify({"error-message": "Error: unknown operation: " + sign})
        return response, 409

@app.route('/stack/arguments', methods=['PUT'])
def add_arguments():
    startTime = requestLogger("PUT", "/stack/arguments")
    stackLogger = logging.getLogger('stack-logger')

    content = request.json
    numbers = content['arguments']
    i = 0
    for number in numbers:
        stack.append(int(number))
        i = i+1
    stackLogger.info("Adding total of %d argument(s) to the stack | Stack size: " + str(len(stack)) + " | request #%d", i, requestNum)
    stackLogger.debug("Adding arguments: %s | Stack size before " + str(len(stack) - i) + " | stack size after " + str(len(stack)) + " | request #%d",str(numbers).replace('[','').replace(']','').replace(' ',''), requestNum)
    requestLoggerEnd(startTime)
    response = jsonify({"result": str(len(stack))})
    return response, 200

@app.route('/independent/calculate', methods=['POST'])
def independent_calc():
    startTime = requestLogger("POST", "/independent/calculate")
    indLogger = logging.getLogger("independent-logger")

    data = request.get_json()
    numbers = data["arguments"]
    sign = data["operation"].lower()

    if sign in one_num_sign:
        if len(numbers) < 1:
            indLogger.error("Server encountered an error ! message: Error: Not enough arguments to perform the operation" + sign + " | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error: Not enough arguments to perform the operation" + sign})
            return response, 409
        elif len(numbers) > 1:
            indLogger.error("Server encountered an error ! message: Error: Too many arguments to perform the operation " + sign + " | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error: Too many arguments to perform the operation " + sign})
            return response, 409
        elif sign == "fact" and (int(numbers[0]) < 0):
            indLogger.error("Server encountered an error ! message: Error while performing operation Factorial: not supported for the negative number" + " | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error while performing operation Factorial: not supported for the negative number"})
            return response, 409
        else:
            result = str(calc(sign, numbers))

            indLogger.info("Performing operation %s. Result is %s" + " | request #%d", sign, result, requestNum)
            indLogger.debug("Performing operation: %s(%s) = %s" + " | request #%d", sign, str(numbers).replace('[','').replace(']','').replace(' ',''), result, requestNum)
            requestLoggerEnd(startTime)

            response = jsonify({"result": result})
            return response, 200


    elif sign in simple_sign:
        if len(numbers) < 2:
            indLogger.error("Server encountered an error ! message: Error: Not enough arguments to perform the operation" + sign + " | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error: Not enough arguments to perform the operation" + sign})
            return response, 409
        elif len(numbers) > 2:
            indLogger.error("Server encountered an error ! message: Error: Too many arguments to perform the operation " + sign + " | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error: Too many arguments to perform the operation " + sign})
            return response, 409
        elif sign == 'divide' and int(numbers[1]) == 0:
            indLogger.error("Server encountered an error ! message: Error while performing operation Divide: division by 0" + " | request #%d", requestNum)
            requestLoggerEnd(startTime)
            response = jsonify({"error-message": "Error while performing operation Divide: division by 0"})
            return response, 409
        else:
            result = str(calc(sign, numbers))

            indLogger.info("Performing operation %s. Result is %s" + " | request #%d", sign, result, requestNum)
            indLogger.debug("Performing operation: %s(%s) = %s" + " | request #%d", sign, str(numbers).replace('[','').replace(']','').replace(' ',''), result, requestNum)
            requestLoggerEnd(startTime)

            response = jsonify({"result": result})
            return response, 200

    else:
        indLogger.error("Server encountered an error ! message: Error: unknown operation: " + sign + " | request #%d", requestNum)
        requestLoggerEnd(startTime)
        response = jsonify({"error-message": "Error: unknown operation: " + sign})
        return response, 409

@app.route('/stack/arguments', methods=['DELETE'])
def delete_from_stack():
    startTime = requestLogger("DELETE", "/stack/arguments")
    stackLogger = logging.getLogger('stack-logger')

    count = int(request.args.get('count'))
    if len(stack) < count:
        stackLogger.error("Server encountered an error ! message: Error: cannot remove " + str(count) + " from the stack. It has only " + str(len(stack)) + " arguments" + " | request #%d", requestNum)
        requestLoggerEnd(startTime)
        response = jsonify({"error-message": "Error: cannot remove " + str(count) + " from the stack. It has only " + str(len(stack)) + " arguments"})
        return response, 409
    for i in range(count):
        stack.pop()
    stackLogger.info("Removing total %d argument(s) from the stack | Stack size: %d" + " | request #%d", count, len(stack), requestNum)
    requestLoggerEnd(startTime)
    response = jsonify({"result": len(stack)})
    return response, 200

@app.route('/logs/level', methods=['GET'])
def get_current_logger_level():
    startTime = requestLogger("GET", "/logs/level")

    loggerName = request.args.get('logger-name')
    if loggerName == "request-logger":
        requestLoggerEnd(startTime)
        response = jsonify({"result": str(reqLogger.getEffectiveLevel())})
        return response, 200
    elif loggerName == "stack-logger":
        requestLoggerEnd(startTime)
        response = jsonify({"result": str(stackLogger.getEffectiveLevel())})
        return response, 200
    elif loggerName == "independent-logger":
        requestLoggerEnd(startTime)
        response = jsonify({"result": str(independentLogger.getEffectiveLevel())})
        return response, 200
    else:
        requestLoggerEnd(startTime)
        response = jsonify({"error-message": "Error: unknown logger name: " + loggerName})
        return response, 409

    requestLoggerEnd(startTime)

@app.route('/logs/level', methods=['PUT'])
def set_logger_level():
    startTime = requestLogger("PUT", "/logs/level")

    reqLogger = logging.getLogger('request-logger')
    indLogger = logging.getLogger('independent-logger')
    stackLogger = logging.getLogger('stack-logger')

    loggerName = request.args.get('logger-name')
    level = request.args.get('logger-level')

    if level == "TRACE":
        logLevel = logging.TRACE
    elif level == "DEBUG":
        logLevel = logging.DEBUG
    elif level == "INFO":
        logLevel = logging.INFO
    elif level == "WARNING":
        logLevel = logging.WARNING
    elif level == "ERROR":
        logLevel = logging.ERROR
    elif level == "FATAL":
        logLevel = logging.FATAL

    if loggerName == "request-logger":
        reqLogger.setLevel(logLevel)
        for handler in reqLogger.handlers:
            handler.setLevel(logLevel)
        requestLoggerEnd(startTime)
        response = jsonify({"result": str(reqLogger.getEffectiveLevel())})
        return response, 200
    
    elif loggerName == "stack-logger":
        stackLogger.setLevel(logLevel)
        for handler in stackLogger.handlers:
            handler.setLevel(logLevel)
        requestLoggerEnd(startTime)
        response = jsonify({"result": str(stackLogger.getEffectiveLevel())})
        return response, 200
    
    elif loggerName == "independent-logger":
        indLogger.setLevel(logLevel)
        for handler in indLogger.handlers:
            handler.setLevel(logLevel)
        requestLoggerEnd(startTime)
        response = jsonify({"result": str(indLogger.getEffectiveLevel())})
        return response, 200
    
    else:
        requestLoggerEnd(startTime)
        response = jsonify({"result": "Error: unknown logger name: " + loggerName})
        return response, 409



def requestLogger(httpVerb, httpResource):
    currTime = round(time.time() * 1000)

    global requestNum
    requestNum = requestNum + 1

    reqLogger = logging.getLogger('request-logger')
    reqLogger.info("Incoming request | #%d | resource: %s | HTTP Verb %s | request #%d", requestNum, httpResource, httpVerb, requestNum)
    
    return currTime

def requestLoggerEnd(startTime):
    totalReqTime = round(time.time() * 1000) - startTime
    reqLogger = logging.getLogger('request-logger')
    reqLogger.debug("request #%d duration: %dms | request #%d", requestNum, totalReqTime, requestNum)

def calc(sign, numbers):
    if sign == "plus":
        return int(numbers[0]) + int(numbers[1])
    elif sign == "minus":
        return int(numbers[0]) - int(numbers[1])
    elif sign == "times":
        return int(numbers[0]) * int(numbers[1])
    elif sign == "divide":
        return int(int(numbers[0]) / int(numbers[1]))
    elif sign == "pow":
        return pow(int(numbers[0]), int(numbers[1]))
    elif sign == "abs":
        return abs(int(numbers[0]))
    elif sign == "fact":
        return math.factorial(numbers[0])


def createLogDirectory():
    if os.path.exists('./logs') and os.path.isdir('./logs'):
        shutil.rmtree('./logs')
    os.mkdir('./logs')

def createLoggers():
    createLogDirectory()
    formatter = logging.Formatter(fmt="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s ", datefmt='%d-%m-%Y %H:%M:%S')

    # request logger
    reqLogger = logging.getLogger('request-logger')
    reqLogger.setLevel(logging.INFO)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)

    fileHandler = logging.FileHandler('logs/requests.log')
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)

    reqLogger.addHandler(consoleHandler)
    reqLogger.addHandler(fileHandler)

    # stack logger
    stackLogger = logging.getLogger('stack-logger')
    stackLogger.setLevel(logging.INFO)

    fileHandler = logging.FileHandler('logs/stack.log')
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    stackLogger.addHandler(fileHandler)

    # independent logger
    indLogger = logging.getLogger('independent-logger')
    indLogger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler('logs/independent.log')
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    indLogger.addHandler(fileHandler)


def main():
    createLoggers()
    logging.getLogger('werkzeug').disabled = True
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()




