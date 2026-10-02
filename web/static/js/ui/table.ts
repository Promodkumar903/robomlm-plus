import type {
  TableOptions,
  TableColumn
} from "./types";

import {
  el,
  text
} from "./dom";

function renderCell<T>(
  column: TableColumn<T>,
  value: unknown,
  row: T
): HTMLElement {
  const cell = el("td");

  if (column.render) {
    const rendered =
      column.render(value, row);

    if (
      typeof rendered === "string"
    ) {
      cell.appendChild(
        text(rendered)
      );
    } else {
      cell.appendChild(
        rendered
      );
    }
  } else {
    cell.appendChild(
      text(value)
    );
  }

  return cell;
}

export function createTable<T>(
  rows: T[],
  options: TableOptions<T>
): HTMLElement {
  const wrapper = el(
    "div",
    "ui-table-wrapper"
  );

  if (rows.length === 0) {
    const empty = el(
      "div",
      "ui-table-empty"
    );

    empty.textContent =
      options.emptyMessage ??
      "No data available.";

    wrapper.appendChild(empty);

    return wrapper;
  }

  const table = el(
    "table",
    "ui-table"
  );

  const thead = el("thead");
  const headerRow = el("tr");

  for (const column of options.columns) {
    const th = el("th");
    th.textContent = column.label;
    headerRow.appendChild(th);
  }

  thead.appendChild(headerRow);

  const tbody = el("tbody");

  for (const row of rows) {
    const tr = el("tr");

    for (const column of options.columns) {
      const value =
        (row as Record<string, unknown>)[
          column.key
        ];

      tr.appendChild(
        renderCell(
          column,
          value,
          row
        )
      );
    }

    tbody.appendChild(tr);
  }

  table.appendChild(thead);
  table.appendChild(tbody);

  wrapper.appendChild(table);

  return wrapper;
}