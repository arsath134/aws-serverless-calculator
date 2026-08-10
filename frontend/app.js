// =====================================================
// API GATEWAY URL
// =====================================================

const API_URL ="Your API INVOKE URL";


// =====================================================
// VARIABLES
// =====================================================

let expression = "";


// =====================================================
// DISPLAY ELEMENTS
// =====================================================

const expressionDisplay =
    document.getElementById(
        "expression"
    );

const resultDisplay =
    document.getElementById(
        "result"
    );

const statusDisplay =
    document.getElementById(
        "status"
    );


// =====================================================
// ADD VALUE TO EXPRESSION
// =====================================================

function addToExpression(value) {

    expression += value;

    expressionDisplay.textContent =
        expression;

    resultDisplay.textContent =
        "0";

    statusDisplay.textContent =
        "Ready";
}


// =====================================================
// CLEAR
// =====================================================

function clearCalculator() {

    expression = "";

    expressionDisplay.textContent =
        "0";

    resultDisplay.textContent =
        "0";

    statusDisplay.textContent =
        "Ready";
}


// =====================================================
// CALCULATE USING AWS LAMBDA
// =====================================================

async function calculate() {

    if (!expression) {

        statusDisplay.textContent =
            "Enter a calculation";

        return;
    }


    resultDisplay.textContent =
        "...";

    statusDisplay.textContent =
        "Sending to AWS Lambda...";


    try {

        // SEND REQUEST TO API GATEWAY

        const response =
            await fetch(
                API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        expression:
                            expression
                    })
                }
            );


        // READ RESPONSE

        let data =
            await response.json();


        console.log(
            "API Gateway response:",
            data
        );


        // API Gateway may return:
        //
        // {
        //   statusCode: 200,
        //   body: "{\"success\":true,...}"
        // }

        if (
            data.body &&
            typeof data.body === "string"
        ) {

            data =
                JSON.parse(
                    data.body
                );
        }


        console.log(
            "Processed Lambda response:",
            data
        );


        // CHECK RESULT

        if (
            !response.ok ||
            data.success !== true
        ) {

            throw new Error(
                data.message ||
                "Calculation failed"
            );
        }


        // SHOW RESULT

        resultDisplay.textContent =
            data.result;


        statusDisplay.textContent =
            "Calculated by AWS Lambda ✓";


        console.log(
            "Calculation ID:",
            data.calculation_id
        );

    }


    catch (error) {

        console.error(
            "Calculation error:",
            error
        );


        resultDisplay.textContent =
            "Error";


        statusDisplay.textContent =
            error.message;
    }
}
