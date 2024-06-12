/**
 * Function to get the curl code for the API
 * @param {string} flowId - The id of the flow
 * @param {boolean} isAuth - If the API is authenticated
 * @returns {string} - The curl code
 */
export function getCurlRunCode(
  flowId: string,
  isAuth: boolean,
  tweaksBuildedObject,
  endpointName?: string,
): string {
  const tweaksObject = tweaksBuildedObject[0];
  // show the endpoint name in the curl command if it exists
  return `curl -X POST \\
    "${window.location.protocol}//${window.location.host}/api/v1/run/${
      endpointName || flowId
    }?stream=false" \\
    -H 'Content-Type: application/json'\\${
      !isAuth ? `\n  -H 'x-api-key: <your api key>'\\` : ""
    }
    -d '{"input_value": "message",
    "output_type": "chat",
    "input_type": "chat",
    "tweaks": ${JSON.stringify(tweaksObject, null, 2)}}'
    `;
}

/**
 * Generates a cURL command for making a POST request to a webhook endpoint.
 *
 * @param {Object} options - The options for generating the cURL command.
 * @param {string} options.flowId - The ID of the flow.
 * @param {boolean} options.isAuth - Indicates whether authentication is required.
 * @param {string} options.endpointName - The name of the webhook endpoint.
 * @returns {string} The cURL command.
 */
export function getCurlWebhookCode(flowId, isAuth, endpointName?: string) {
  return `curl -X POST \\
  "${window.location.protocol}//${window.location.host}/api/v1/webhook/${
    endpointName || flowId
  }" \\
  -H 'Content-Type: application/json'\\${
    !isAuth ? `\n  -H 'x-api-key: <your api key>'\\` : ""
  }
  -d '{"any": "data"}'
  `;
}
