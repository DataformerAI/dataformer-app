import "ag-grid-community/styles/ag-grid.css"; // Mandatory CSS required by the grid
import "ag-grid-community/styles/ag-theme-quartz.css"; // Optional Theme applied to the grid
import { AgGridReact, AgGridReactProps } from "ag-grid-react";
import { ElementRef, forwardRef, useRef, useState } from "react";
import {
  DEFAULT_TABLE_ALERT_MSG,
  DEFAULT_TABLE_ALERT_TITLE,
} from "../../constants/constants";
import { useDarkStore } from "../../stores/darkStore";
import "../../style/ag-theme-shadcn.css"; // Custom CSS applied to the grid
import { cn, toTitleCase } from "../../utils/utils";
import ForwardedIconComponent from "../genericIconComponent";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import TableOptions from "./components/TableOptions";
import resetGrid from "./utils/reset-grid-columns";
import Loading from "../ui/loading";

interface TableComponentProps extends AgGridReactProps {
  columnDefs: NonNullable<AgGridReactProps["columnDefs"]>;
  rowData: NonNullable<AgGridReactProps["rowData"]>;
  alertTitle?: string;
  alertDescription?: string;
  editable?: boolean | string[];
  pagination?: boolean;
  onDelete?: () => void;
  onDuplicate?: () => void;
}

const TableComponent = forwardRef<
  ElementRef<typeof AgGridReact>,
  TableComponentProps
>(
  (
    {
      alertTitle = DEFAULT_TABLE_ALERT_TITLE,
      alertDescription = DEFAULT_TABLE_ALERT_MSG,
      ...props
    },
    ref,
  ) => {
    let colDef = props.columnDefs.map((col, index) => {
      let newCol = {
        ...col,
        headerName: toTitleCase(col.headerName),
      };
      if (index === props.columnDefs.length - 1) {
        newCol = {
          ...newCol,
          resizable: false,
        };
      }
      if (props.onSelectionChanged && index === 0) {
        newCol = {
          ...newCol,
          checkboxSelection: true,
          headerCheckboxSelection: true,
          headerCheckboxSelectionFilteredOnly: true,
        };
      }
      if (
        (typeof props.editable === "boolean" && props.editable) ||
        (Array.isArray(props.editable) &&
          props.editable.includes(newCol.headerName ?? ""))
      ) {
        newCol = {
          ...newCol,
          editable: true,
        };
      }
      return newCol;
    });
    const gridRef = useRef(null);
    // @ts-ignore
    const realRef: React.MutableRefObject<AgGridReact> = ref?.current
      ? ref
      : gridRef;
    const dark = useDarkStore((state) => state.dark);
    const initialColumnDefs = useRef(colDef);
    const [columnStateChange, setColumnStateChange] = useState(false);
    const storeReference = props.columnDefs.map((e) => e.headerName).join("_");
    const makeLastColumnNonResizable = (columnDefs) => {
      columnDefs.forEach((colDef, index) => {
        colDef.resizable = index !== columnDefs.length - 1;
      });
      return columnDefs;
    };

    const onGridReady = (params) => {
      // @ts-ignore
      realRef.current = params;
      const updatedColumnDefs = makeLastColumnNonResizable([...colDef]);
      params.api.setGridOption("columnDefs", updatedColumnDefs);
      const customInit = localStorage.getItem(storeReference);
      initialColumnDefs.current = params.api.getColumnDefs();
      if (customInit && realRef.current) {
        realRef.current.api.applyColumnState({
          state: JSON.parse(customInit),
          applyOrder: true,
        });
      }
      setTimeout(() => {
        if (customInit && realRef.current) {
          setColumnStateChange(true);
        } else {
          setColumnStateChange(false);
        }
      }, 50);
      setTimeout(() => {
        realRef.current.api.hideOverlay();
      }, 1000);
      if (props.onGridReady) props.onGridReady(params);
    };
    const onColumnMoved = (params) => {
      const updatedColumnDefs = makeLastColumnNonResizable(
        params.columnApi.getAllGridColumns().map((col) => col.getColDef()),
      );
      params.api.setGridOption("columnDefs", updatedColumnDefs);
      if (props.onColumnMoved) props.onColumnMoved(params);
    };
    if (props.rowData.length === 0) {
      return (
        <div className="flex h-full w-full items-center justify-center rounded-md border">
          <Alert variant={"default"} className="w-fit">
            <ForwardedIconComponent
              name="AlertCircle"
              className="h-5 w-5 text-primary"
            />
            <AlertTitle>{alertTitle}</AlertTitle>
            <AlertDescription>{alertDescription}</AlertDescription>
          </Alert>
        </div>
      );
    }
    return (
      <div
        className={cn(
          dark ? "ag-theme-quartz-dark" : "ag-theme-quartz",
          "ag-theme-shadcn flex h-full flex-col",
          "relative",
        )} // applying the grid theme
      >
        <AgGridReact
          {...props}
          defaultColDef={{
            minWidth: 100,
            autoHeight: true,
          }}
          columnDefs={colDef}
          ref={realRef}
          onGridReady={onGridReady}
          onColumnMoved={onColumnMoved}
          onStateUpdated={(e) => {
            if (e.sources.some((source) => source.includes("column"))) {
              localStorage.setItem(
                storeReference,
                JSON.stringify(realRef.current?.api?.getColumnState()),
              );
              setColumnStateChange(true);
            }
          }}
        />
        {props.pagination && (
          <TableOptions
            stateChange={columnStateChange}
            hasSelection={realRef.current?.api?.getSelectedRows().length > 0}
            duplicateRow={props.onDuplicate ? props.onDuplicate : undefined}
            deleteRow={props.onDelete ? props.onDelete : undefined}
            resetGrid={() => {
              resetGrid(realRef, initialColumnDefs);
              setTimeout(() => {
                setColumnStateChange(false);
                localStorage.removeItem(storeReference);
              }, 100);
            }}
          />
        )}
      </div>
    );
  },
);

export default TableComponent;
