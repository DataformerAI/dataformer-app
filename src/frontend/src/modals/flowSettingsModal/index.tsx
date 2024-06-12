import { useEffect, useState } from "react";
import EditFlowSettings from "../../components/editFlowSettingsComponent";
import IconComponent from "../../components/genericIconComponent";
import { SETTINGS_DIALOG_SUBTITLE } from "../../constants/constants";
import useAlertStore from "../../stores/alertStore";
import useFlowsManagerStore from "../../stores/flowsManagerStore";
import { FlowSettingsPropsType } from "../../types/components";
import { FlowType } from "../../types/flow";
import BaseModal from "../baseModal";

export default function FlowSettingsModal({
  open,
  setOpen,
}: FlowSettingsPropsType): JSX.Element {
  const saveFlow = useFlowsManagerStore((state) => state.saveFlow);
  const currentFlow = useFlowsManagerStore((state) => state.currentFlow);
  const flows = useFlowsManagerStore((state) => state.flows);
  useEffect(() => {
    setName(currentFlow!.name);
    setDescription(currentFlow!.description);
  }, [currentFlow!.name, currentFlow!.description, open]);

  const [name, setName] = useState(currentFlow!.name);
  const [description, setDescription] = useState(currentFlow!.description);
  const [endpoint_name, setEndpointName] = useState(currentFlow!.endpoint_name);
  const [isSaving, setIsSaving] = useState(false);
  function handleClick(): void {
    setIsSaving(true);
    currentFlow!.name = name;
    currentFlow!.description = description;
    currentFlow!.endpoint_name = endpoint_name;
    saveFlow(currentFlow!)
      ?.then(() => {
        setOpen(false);
        setIsSaving(false);
      })
      .catch((err) => {
        useAlertStore.getState().setErrorData({
          title: "Error while saving changes",
          list: [err?.response?.data.detail ?? ""],
        });
        console.error(err);
      });
  }

  const [nameLists, setNameList] = useState<string[]>([]);

  useEffect(() => {
    const tempNameList: string[] = [];
    flows.forEach((flow: FlowType) => {
      if ((flow.is_component ?? false) === false) tempNameList.push(flow.name);
    });
    setNameList(tempNameList.filter((name) => name !== currentFlow!.name));
  }, [flows]);

  return (
    <BaseModal
      open={open}
      setOpen={setOpen}
      size="smaller-h-full"
      onSubmit={handleClick}
    >
      <BaseModal.Header description={SETTINGS_DIALOG_SUBTITLE}>
        <span className="pr-2">Settings</span>
        <IconComponent name="Settings2" className="mr-2 h-4 w-4 " />
      </BaseModal.Header>
      <BaseModal.Content>
        <EditFlowSettings
          invalidNameList={nameLists}
          name={name}
          description={description}
          endpointName={endpoint_name}
          setName={setName}
          setDescription={setDescription}
          setEndpointName={setEndpointName}
        />
      </BaseModal.Content>

      <BaseModal.Footer
        submit={{
          label: "Save",
          disabled: nameLists.includes(name) && name !== currentFlow!.name,
          dataTestId: "save-flow-settings",
          loading: isSaving,
        }}
      />
    </BaseModal>
  );
}
