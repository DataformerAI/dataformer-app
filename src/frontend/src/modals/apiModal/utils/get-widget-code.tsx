/**
 * Function to get the widget code for the API
 * @param {string} flow - The current flow.
 * @returns {string} - The widget code
 */
export default function getWidgetCode(
  flowId: string,
  flowName: string,
  isAuth: boolean,
): string {
  return `<script src="https://cdn.jsdelivr.net/gh/dfapp-ai/dfapp-embedded-chat@1.0_alpha/dist/build/static/js/bundle.min.js"></script>

  <dfapp-chat
    window_title="${flowName}"
    flow_id="${flowId}"
    host_url="http://localhost:7860"${
      !isAuth
        ? `
    api_key="..."`
        : ""
    }

  ></dfapp-chat>`;
}
