(function (root) {
    function clear(grid, field, container, dateRegistry) {
        container.querySelectorAll("input[type='checkbox']").forEach(input => {
            input.checked = false;
            input.indeterminate = false;
        });
        const dateFilter = dateRegistry && dateRegistry[field];
        if (dateFilter) {
            grid.removeFilter(dateFilter);
            delete dateRegistry[field];
        }
        grid.getFilters().forEach(filter => {
            if (filter.field === field && filter.type === 'in') {
                grid.removeFilter(filter.field, filter.type, filter.value);
            }
        });
        const column = grid.getColumn(field);
        if (column && column.getDefinition().headerFilter) grid.setHeaderFilterValue(field, '');
    }
    root.modusColumnFilters = {clear};
    if (typeof module !== 'undefined' && module.exports) module.exports = {clear};
})(typeof window !== 'undefined' ? window : globalThis);
