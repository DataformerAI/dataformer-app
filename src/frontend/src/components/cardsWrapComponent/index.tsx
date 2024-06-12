import { useEffect, useState } from "react";
import IconComponent from "../../components/genericIconComponent";
import { cn } from "../../utils/utils";

export default function CardsWrapComponent({
  onFileDrop,
  children,
  dragMessage,
}: {
  onFileDrop?: (e: any) => void;
  children: JSX.Element | JSX.Element[];
  dragMessage?: string;
}) {
  const [isDragging, setIsDragging] = useState(false);
  useEffect(() => {
    // Function to handle visibility change
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        // Reset hover state or perform any necessary actions when the tab becomes visible again
        setIsDragging(false);
      }
    };

    // Add event listener for visibility change
    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Cleanup event listener on component unmount
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  const dragOver = (e) => {
    e.preventDefault();
    if (e.dataTransfer.types.some((types) => types === "Files") && onFileDrop) {
      setIsDragging(true);
    }
  };

  const dragEnter = (e) => {
    if (e.dataTransfer.types.some((types) => types === "Files") && onFileDrop) {
      setIsDragging(true);
    }
    e.preventDefault();
  };

  const dragLeave = (e) => {
    e.preventDefault();
    if (onFileDrop) setIsDragging(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    if (onFileDrop) onFileDrop(e);
    setIsDragging(false);
  };

  return (
    <div
      onDragOver={dragOver}
      onDragEnter={dragEnter}
      onDragLeave={dragLeave}
      onDrop={onDrop}
      className={cn(
        "h-full w-full",
        isDragging
          ? "mb-36 flex flex-col items-center justify-center gap-4 text-2xl font-light"
          : "",
      )}
    >
      {isDragging ? (
        <>
          <IconComponent name="ArrowUpToLine" className="h-12 w-12 stroke-1" />
          {dragMessage ? dragMessage : "Drop your file here"}
        </>
      ) : (
        children
      )}
    </div>
  );
}
