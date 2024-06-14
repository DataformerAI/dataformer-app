import ForwardedIconComponent from "../../../../../../components/genericIconComponent";
import RecordsOutputComponent from "../../../../../../components/recordsOutputComponent";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "../../../../../../components/ui/alert";
import { Case } from "../../../../../../shared/components/caseComponent";
import TextOutputView from "../../../../../../shared/components/textOutputView";
import useFlowStore from "../../../../../../stores/flowStore";
import ErrorOutput from "./components";
import { useState, useEffect } from "react";

export default function SwitchOutputView(nodeId): JSX.Element {
  const nodeIdentity = nodeId.nodeId;

  const nodes = useFlowStore((state) => state.nodes);
  const flowPool = useFlowStore((state) => state.flowPool);
  const node = nodes.find((node) => node?.id === nodeIdentity);

  console.log(`node`, node);
  const datasetNameValue = node.data?.node?.template?.dataset_name?.value;
  console.log(`Dataset Name Value: `, datasetNameValue);

  const [data, setData] = useState([]);

  useEffect(() => {
    if (datasetNameValue) {
      fetch(`/${datasetNameValue}_train.jsonl`)
        .then((response) => response.text())
        .then((text) => {
          const lines = text.split("\n");
          const jsonlData = lines
            .filter((line) => line.trim() !== "")
            .map((line) => JSON.parse(line));
          setData(jsonlData);
        });
    }
  }, [datasetNameValue]);

  return (
    <RecordsOutputComponent rows={data} pagination={true} columnMode="union" />
  );
}
