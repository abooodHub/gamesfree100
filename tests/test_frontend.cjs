const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = vm.createContext({ document: { addEventListener() {} }, localStorage: { getItem() { return null; } }, Date, URL });
vm.runInContext(fs.readFileSync(path.join(__dirname, '../script.js'), 'utf8'), context);
const now = Date.parse('2026-09-08T12:00:00Z');
const state = (source, unavailable = false) => context.storeHealthState(source, unavailable, now);
test('store health distinguishes success, delay, failure, and unavailable status', () => {
    const recent = { status: 'ok', last_success: '2026-09-08T11:00:00Z' };
    assert.equal(state(recent), 'ok');
    assert.equal(state({ ...recent, last_success: '2026-09-08T00:00:00Z' }), 'stale');
    assert.equal(state({ ...recent, status: 'error' }), 'error');
    assert.equal(state(recent, true), 'unknown');
    assert.equal(state({ status: 'ok', last_success: 'invalid' }), 'unknown');
    assert.equal(state({ ...recent, last_success: '2026-09-09T00:00:00Z' }), 'unknown');
    assert.equal(state(null), 'unknown');
});
test('one store failure does not change the other store status', () => {
    assert.equal(state({ status: 'error', last_success: '2026-09-08T10:00:00Z' }), 'error');
    assert.equal(state({ status: 'ok', last_success: '2026-09-08T11:00:00Z' }), 'ok');
});
