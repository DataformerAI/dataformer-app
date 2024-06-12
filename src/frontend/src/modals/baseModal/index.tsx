import { ReactNode, useEffect } from "react";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../components/ui/dialog";

import {
  Dialog as Modal,
  DialogContent as ModalContent,
} from "../../components/ui/dialog-with-no-close";

import { DialogClose } from "@radix-ui/react-dialog";
import * as Form from "@radix-ui/react-form";
import { Button } from "../../components/ui/button";
import { modalHeaderType } from "../../types/components";
import { cn } from "../../utils/utils";
import { switchCaseModalSize } from "./helpers/switch-case-size";

type ContentProps = { children: ReactNode; overflowHidden?: boolean };
type HeaderProps = { children: ReactNode; description: string };
type FooterProps = { children: ReactNode };
type TriggerProps = {
  children: ReactNode;
  asChild?: boolean;
  disable?: boolean;
  className?: string;
};

const Content: React.FC<ContentProps> = ({ children, overflowHidden }) => {
  return (
    <div
      className={cn(
        `flex w-full flex-grow flex-col transition-all duration-300`,
        overflowHidden ? "overflow-hidden" : "overflow-visible",
      )}
    >
      {children}
    </div>
  );
};
const Trigger: React.FC<TriggerProps> = ({
  children,
  asChild,
  disable,
  className,
}) => {
  return (
    <DialogTrigger
      className={asChild ? "" : cn("w-full", className)}
      hidden={children ? false : true}
      disabled={disable}
      asChild={asChild}
    >
      {children}
    </DialogTrigger>
  );
};

const Header: React.FC<{
  children: ReactNode;
  description: string | JSX.Element | null;
}> = ({ children, description }: modalHeaderType): JSX.Element => {
  return (
    <DialogHeader>
      <DialogTitle className="line-clamp-1 flex items-center">
        {children}
      </DialogTitle>
      <DialogDescription className="line-clamp-2">
        {description}
      </DialogDescription>
    </DialogHeader>
  );
};

const Footer: React.FC<{
  children?: ReactNode;
  submit?: {
    label: string;
    icon?: ReactNode;
    loading?: boolean;
    disabled?: boolean;
    dataTestId?: string;
    onClick?: () => void;
  };
}> = ({ children, submit }) => {
  return (
    <div className="flex flex-shrink-0 flex-row-reverse">
      {submit ? (
        <div className="flex w-full items-center justify-between">
          {children ?? <div />}
          <div className="flex items-center gap-3">
            <DialogClose asChild>
              <Button variant="outline" type="button">
                Cancel
              </Button>
            </DialogClose>
            <Button
              data-testid={submit.dataTestId}
              type={submit.onClick ? "button" : "submit"}
              onClick={submit.onClick}
              loading={submit.loading}
            >
              {submit.icon && submit.icon}
              {submit.label}
            </Button>
          </div>
        </div>
      ) : (
        <>{children && children}</>
      )}
    </div>
  );
};
interface BaseModalProps {
  children: [
    React.ReactElement<ContentProps>,
    React.ReactElement<HeaderProps>,
    React.ReactElement<TriggerProps>?,
    React.ReactElement<FooterProps>?,
  ];
  open?: boolean;
  setOpen?: (open: boolean) => void;
  size?:
    | "x-small"
    | "smaller"
    | "small"
    | "medium"
    | "medium-tall"
    | "large"
    | "three-cards"
    | "large-thin"
    | "large-h-full"
    | "small-h-full"
    | "medium-h-full"
    | "md-thin"
    | "sm-thin"
    | "smaller-h-full"
    | "medium-log";

  disable?: boolean;
  onChangeOpenModal?: (open?: boolean) => void;
  type?: "modal" | "dialog";
  onSubmit?: () => void;
}
function BaseModal({
  open,
  setOpen,
  children,
  size = "large",
  onChangeOpenModal,
  type = "dialog",
  onSubmit,
}: BaseModalProps) {
  const headerChild = React.Children.toArray(children).find(
    (child) => (child as React.ReactElement).type === Header,
  );
  const triggerChild = React.Children.toArray(children).find(
    (child) => (child as React.ReactElement).type === Trigger,
  );
  const ContentChild = React.Children.toArray(children).find(
    (child) => (child as React.ReactElement).type === Content,
  );
  const ContentFooter = React.Children.toArray(children).find(
    (child) => (child as React.ReactElement).type === Footer,
  );

  let { minWidth, height } = switchCaseModalSize(size);

  useEffect(() => {
    if (onChangeOpenModal) {
      onChangeOpenModal(open);
    }
  }, [open]);

  const modalContent = (
    <>
      {headerChild}
      {ContentChild}
      {ContentFooter && ContentFooter}
    </>
  );

  const contentClasses = cn(
    minWidth,
    height,
    "flex flex-col duration-300 overflow-hidden",
  );

  //UPDATE COLORS AND STYLE CLASSSES
  return (
    <>
      {type === "modal" ? (
        <Modal open={open} onOpenChange={setOpen}>
          {triggerChild}
          <ModalContent className={contentClasses}>{modalContent}</ModalContent>
        </Modal>
      ) : (
        <Dialog open={open} onOpenChange={setOpen}>
          {triggerChild}
          <DialogContent className={contentClasses}>
            {onSubmit ? (
              <Form.Root
                onSubmit={(event) => {
                  event.preventDefault();
                  onSubmit();
                }}
                className="flex h-full flex-col gap-6"
              >
                {modalContent}
              </Form.Root>
            ) : (
              modalContent
            )}
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}

BaseModal.Content = Content;
BaseModal.Header = Header;
BaseModal.Trigger = Trigger;
BaseModal.Footer = Footer;
export default BaseModal;
