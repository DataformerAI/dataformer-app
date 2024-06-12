import ForwardedIconComponent from "../../../../../../../components/genericIconComponent";
import { Button } from "../../../../../../../components/ui/button";

const UploadFileButton = ({
  fileInputRef,
  handleFileChange,
  handleButtonClick,
  lockChat,
}) => {
  return (
    <div>
      <input
        disabled={lockChat}
        type="file"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
      <Button
        disabled={lockChat}
        className={`font-bold text-white transition-all ${
          lockChat ? "cursor-not-allowed" : "hover:text-muted-foreground"
        }`}
        onClick={handleButtonClick}
        variant="none"
        size="none"
      >
        <ForwardedIconComponent name="PaperclipIcon" />
      </Button>
    </div>
  );
};

export default UploadFileButton;
