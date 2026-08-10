import json
import boto3
import uuid
import ast
import operator
import math
from datetime import datetime, timezone


# =========================================================
# DYNAMODB
# =========================================================

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("calculations")


# =========================================================
# ALLOWED OPERATORS
# =========================================================

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow
}


# =========================================================
# CALCULATE MATHEMATICAL EXPRESSION
# =========================================================

def calculate_expression(expression):

    # Convert calculator symbols to Python operators
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("^", "**")

    # Parse expression safely
    tree = ast.parse(
        expression,
        mode="eval"
    )

    def evaluate(node):

        # Expression
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        # Numbers
        if isinstance(
            node,
            ast.Constant
        ):

            if isinstance(
                node.value,
                (int, float)
            ):
                return node.value

            raise ValueError(
                "Invalid number"
            )

        # Positive / negative numbers
        if isinstance(
            node,
            ast.UnaryOp
        ):

            value = evaluate(
                node.operand
            )

            if isinstance(
                node.op,
                ast.USub
            ):
                return -value

            if isinstance(
                node.op,
                ast.UAdd
            ):
                return value

            raise ValueError(
                "Invalid unary operator"
            )

        # Mathematical operations
        if isinstance(
            node,
            ast.BinOp
        ):

            left = evaluate(
                node.left
            )

            right = evaluate(
                node.right
            )

            operation = OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "Operator not allowed"
                )

            # Division by zero
            if (
                isinstance(
                    node.op,
                    ast.Div
                )
                and right == 0
            ):
                raise ValueError(
                    "Cannot divide by zero"
                )

            return operation(
                left,
                right
            )

        # Square root
        if isinstance(
            node,
            ast.Call
        ):

            if (
                isinstance(
                    node.func,
                    ast.Name
                )
                and node.func.id == "sqrt"
                and len(node.args) == 1
            ):

                value = evaluate(
                    node.args[0]
                )

                if value < 0:
                    raise ValueError(
                        "Cannot calculate square root of a negative number"
                    )

                return math.sqrt(value)

        raise ValueError(
            "Invalid mathematical expression"
        )

    return evaluate(tree)


# =========================================================
# IDENTIFY OPERATION
# =========================================================

def identify_operation(expression):

    if "+" in expression:
        return "addition"

    if "-" in expression:
        return "subtraction"

    if (
        "×" in expression
        or "*" in expression
    ):
        return "multiplication"

    if (
        "÷" in expression
        or "/" in expression
    ):
        return "division"

    if "%" in expression:
        return "modulo"

    if (
        "^" in expression
        or "**" in expression
    ):
        return "power"

    if "sqrt" in expression:
        return "square_root"

    return "calculation"


# =========================================================
# API RESPONSE
# =========================================================

def create_response(
    status_code,
    data
):

    return {
        "statusCode": status_code,

        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },

        "body": json.dumps(data)
    }


# =========================================================
# GET REQUEST BODY
# =========================================================

def get_request_body(event):

    # API Gateway sends:
    #
    # {
    #     "expression": "25 + 15"
    # }

    if event.get("expression") is not None:

        return event


    # API Gateway can also send:
    #
    # {
    #     "body": "{\"expression\":\"25 + 15\"}"
    # }

    body = event.get("body")

    if body is None:

        return {}


    # Body is JSON string
    if isinstance(
        body,
        str
    ):

        return json.loads(
            body
        )


    # Body is already JSON object
    if isinstance(
        body,
        dict
    ):

        return body


    return {}


# =========================================================
# LAMBDA HANDLER
# =========================================================

def lambda_handler(
    event,
    context
):

    print(
        "Received event:"
    )

    print(
        json.dumps(event)
    )


    try:

        # Get request body
        body = get_request_body(
            event
        )


        # Get expression
        expression = body.get(
            "expression"
        )


        if expression is None:

            return create_response(
                400,
                {
                    "success": False,
                    "message":
                        "Expression is required"
                }
            )


        # Convert to string
        expression = str(
            expression
        ).strip()


        if expression == "":

            return create_response(
                400,
                {
                    "success": False,
                    "message":
                        "Expression cannot be empty"
                }
            )


        # Calculate
        result = calculate_expression(
            expression
        )


        # Create calculation ID
        calculation_id = (
            "CALC-"
            + str(
                uuid.uuid4()
            )[:8]
        )


        # Timestamp
        timestamp = datetime.now(
            timezone.utc
        ).isoformat()


        # Identify operation
        operation = identify_operation(
            expression
        )


        # DynamoDB item
        item = {

            "calculations_id":
                calculation_id,

            "expression":
                expression,

            "result":
                result,

            "operation":
                operation,

            "timestamp":
                timestamp
        }


        print(
            "Saving item:"
        )

        print(
            json.dumps(item)
        )


        # Save to DynamoDB
        table.put_item(
            Item=item
        )


        print(
            "Calculation saved successfully"
        )


        # Return result
        return create_response(
            200,
            {

                "success":
                    True,

                "calculation_id":
                    calculation_id,

                "expression":
                    expression,

                "result":
                    result,

                "operation":
                    operation,

                "timestamp":
                    timestamp
            }
        )


    except ZeroDivisionError:

        return create_response(
            400,
            {
                "success": False,
                "message":
                    "Cannot divide by zero"
            }
        )


    except (
        SyntaxError,
        ValueError
    ) as e:

        print(
            "Calculation error:",
            str(e)
        )

        return create_response(
            400,
            {
                "success": False,
                "message":
                    "Invalid mathematical expression",
                "error":
                    str(e)
            }
        )


    except Exception as e:

        print(
            "Unexpected error:",
            str(e)
        )

        return create_response(
            500,
            {
                "success": False,
                "message":
                    "Internal server error",
                "error":
                    str(e)
            }
        )
