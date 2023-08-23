import {ComponentProps, CSSProperties, forwardRef} from 'react';
import classNames from 'classnames';

import FileSize from 'sentry/components/fileSize';
import {
  ButtonWrapper,
  Cell,
  Text,
} from 'sentry/components/replays/virtualizedGrid/bodyCell';
import {Tooltip} from 'sentry/components/tooltip';
import {IconCircleFill, IconFatal, IconFire, IconWarning} from 'sentry/icons';
import type useCrumbHandlers from 'sentry/utils/replays/hooks/useCrumbHandlers';
import {
  getFrameImpact,
  getFramePath,
  getFrameType,
} from 'sentry/utils/replays/resourceFrame';
import type {SpanFrame} from 'sentry/utils/replays/types';
import useUrlParams from 'sentry/utils/useUrlParams';
import useSortAccessibility from 'sentry/views/replays/detail/accessibility/useSortAccessibility';
import TimestampButton from 'sentry/views/replays/detail/timestampButton';
import {operationName} from 'sentry/views/replays/detail/utils';

const EMPTY_CELL = '--';

const IMPACT_COLOR_MAPPINGS = {
  minor: <IconWarning color="yellow400" />,
  moderate: <IconWarning color="yellow400" />,
  serious: <IconFire color="pink400" />,
  critical: <IconFatal color="red400" />,
};

interface Props extends ReturnType<typeof useCrumbHandlers> {
  columnIndex: number;
  currentHoverTime: number | undefined;
  currentTime: number;
  frame: SpanFrame;
  onClickCell: (props: {dataIndex: number; rowIndex: number}) => void;
  rowIndex: number;
  sortConfig: ReturnType<typeof useSortAccessibility>['sortConfig'];
  startTimestampMs: number;
  style: CSSProperties;
}

const AccessibilityTableCell = forwardRef<HTMLDivElement, Props>(
  (
    {
      columnIndex,
      currentHoverTime,
      currentTime,
      frame,
      onMouseEnter,
      onMouseLeave,
      onClickCell,
      onClickTimestamp,
      rowIndex,
      sortConfig,
      startTimestampMs,
      style,
    }: Props,
    ref
  ) => {
    // Rows include the sortable header, the dataIndex does not
    const dataIndex = rowIndex - 1;

    const {getParamValue} = useUrlParams('n_detail_row', '');
    const isSelected = getParamValue() === String(dataIndex);

    const type = getFrameType(frame);
    const impact = getFrameImpact(frame);
    const path = getFramePath(frame);

    const hasOccurred = currentTime >= frame.offsetMs;
    const isBeforeHover =
      currentHoverTime === undefined || currentHoverTime >= frame.offsetMs;

    const isByTimestamp = sortConfig.by === 'startTimestamp';
    const isAsc = isByTimestamp ? sortConfig.asc : undefined;
    const columnProps = {
      className: classNames({
        beforeCurrentTime: isByTimestamp
          ? isAsc
            ? hasOccurred
            : !hasOccurred
          : undefined,
        afterCurrentTime: isByTimestamp
          ? isAsc
            ? !hasOccurred
            : hasOccurred
          : undefined,
        beforeHoverTime:
          isByTimestamp && currentHoverTime !== undefined
            ? isAsc
              ? isBeforeHover
              : !isBeforeHover
            : undefined,
        afterHoverTime:
          isByTimestamp && currentHoverTime !== undefined
            ? isAsc
              ? !isBeforeHover
              : isBeforeHover
            : undefined,
      }),
      hasOccurred: isByTimestamp ? hasOccurred : undefined,
      isSelected,
      isStatusError: typeof statusCode === 'number' && statusCode >= 400,
      onClick: () => onClickCell({dataIndex, rowIndex}),
      onMouseEnter: () => onMouseEnter(frame),
      onMouseLeave: () => onMouseLeave(frame),
      ref,
      style,
    } as ComponentProps<typeof Cell>;

    const renderFns = [
      () => (
        <Cell {...columnProps}>
          <Text>
            <Tooltip title={impact ? impact : 'unknown'}>
              {IMPACT_COLOR_MAPPINGS[impact]}
            </Tooltip>
          </Text>
        </Cell>
      ),
      () => (
        <Cell {...columnProps}>
          <Text>{type ? type : 'unknown'}</Text>
        </Cell>
      ),
      () => (
        <Cell {...columnProps}>
          <Text>{path ? path : EMPTY_CELL}</Text>
        </Cell>
      ),
      () => (
        <Cell {...columnProps}>
          <Tooltip
            title={frame.timestamp}
            isHoverable
            showOnlyOnOverflow
            overlayStyle={{maxWidth: '500px !important'}}
          >
            <Text>{frame.timestamp || EMPTY_CELL}</Text>
          </Tooltip>
        </Cell>
      ),
      () => (
        <Cell {...columnProps}>
          <Tooltip title={operationName(frame.op)} isHoverable showOnlyOnOverflow>
            <Text>{operationName(frame.op)}</Text>
          </Tooltip>
        </Cell>
      ),
      () => (
        <Cell {...columnProps} numeric>
          <ButtonWrapper>
            <TimestampButton
              format="mm:ss.SSS"
              onClick={event => {
                event.stopPropagation();
                onClickTimestamp(frame);
              }}
              startTimestampMs={startTimestampMs}
              timestampMs={frame.timestampMs}
            />
          </ButtonWrapper>
        </Cell>
      ),
    ];

    return renderFns[columnIndex]();
  }
);

export default AccessibilityTableCell;