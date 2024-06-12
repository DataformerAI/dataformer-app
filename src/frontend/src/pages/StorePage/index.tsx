import PageLayout from "../../components/pageLayout";
import { STORE_DESC, STORE_TITLE } from "../../constants/constants";

export default function StorePage(): JSX.Element {
  return (
    <PageLayout
      betaIcon
      title={STORE_TITLE}
      description={STORE_DESC}
    >
      <div className="flex h-full w-full items-center justify-center">
        <h1 className="text-xl font-bold">Coming Soon</h1>
      </div>
    </PageLayout>
  );
}