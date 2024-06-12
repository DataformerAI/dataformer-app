import { uniqueId } from "lodash";
import { useContext, useEffect, useState } from "react";
import CollectionCardComponent from "../../components/cardComponent";
import IconComponent from "../../components/genericIconComponent";
import PageLayout from "../../components/pageLayout";
import ShadTooltip from "../../components/shadTooltipComponent";
import { SkeletonCardComponent } from "../../components/skeletonCardComponent";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";

import { Link, useNavigate, useParams } from "react-router-dom";
import PaginatorComponent from "../../components/paginatorComponent";
import { TagsSelector } from "../../components/tagsSelectorComponent";
import { Badge } from "../../components/ui/badge";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../components/ui/select";
import {
  APIKEY_ERROR_ALERT,
  COMPONENTS_ERROR_ALERT,
  INVALID_API_ERROR_ALERT,
  NOAPI_ERROR_ALERT,
} from "../../constants/alerts_constants";
import { STORE_DESC, STORE_TITLE } from "../../constants/constants";
import { AuthContext } from "../../contexts/authContext";
import { getStoreComponents, getStoreTags } from "../../controllers/API";
import StoreApiKeyModal from "../../modals/storeApiKeyModal";
import useAlertStore from "../../stores/alertStore";
import useFlowsManagerStore from "../../stores/flowsManagerStore";
import { useStoreStore } from "../../stores/storeStore";
import { storeComponent } from "../../types/store";
import { cn } from "../../utils/utils";

export default function StorePage(): JSX.Element {
  return (
    <PageLayout
      betaIcon
      title="Dataformer App StoreBETA"
      description="Explore community-shared flows and components."
    >
      <div className="flex h-full w-full items-center justify-center">
        <h1 className="text-xl font-bold">Coming soon</h1>
      </div>
    </PageLayout>
  );
}
