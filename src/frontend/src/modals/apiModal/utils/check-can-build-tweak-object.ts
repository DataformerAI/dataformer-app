import { DFAPP_SUPPORTED_TYPES } from "../../../constants/constants";

export const checkCanBuildTweakObject = (element, templateField) => {
  return (
    element.data.node.template[templateField] &&
    templateField.charAt(0) !== "_" &&
    element.data.node.template[templateField].show &&
    DFAPP_SUPPORTED_TYPES.has(
      element.data.node.template[templateField].type,
    ) &&
    templateField !== "code"
  );
};
