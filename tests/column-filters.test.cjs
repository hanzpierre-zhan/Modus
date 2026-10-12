const assert = require('node:assert/strict');
const {clear} = require('../static/js/column-filters.js');
const dateFn = () => true;
const otherFn = () => true;
const inputs = [{checked:true,indeterminate:false},{checked:false,indeterminate:true}];
let filters = [{field:'status',type:'in',value:['Running']},{field:'project',type:'in',value:['FLM']},{field:dateFn},{field:otherFn}];
const headers = {status:'Running',project:'FLM'};
const grid = {
    getFilters:()=>filters.slice(),
    removeFilter(field,type,value){filters=filters.filter(f=>!(f.field===field && (type===undefined || (f.type===type && f.value===value))));},
    getColumn:()=>({getDefinition:()=>({headerFilter:'input'})}),
    setHeaderFilterValue:(field,value)=>headers[field]=value
};
const registry = {status:dateFn};
clear(grid,'status',{querySelectorAll:()=>inputs},registry);
assert.deepEqual(inputs,[{checked:false,indeterminate:false},{checked:false,indeterminate:false}]);
assert.deepEqual(filters,[{field:'project',type:'in',value:['FLM']},{field:otherFn}]);
assert.deepEqual(headers,{status:'',project:'FLM'});
assert.deepEqual(registry,{});
clear(grid,'status',{querySelectorAll:()=>[]},registry);
assert.equal(filters.length,2);
console.log('Limpiar reinicia selección, texto y fecha sin quitar otros filtros.');
