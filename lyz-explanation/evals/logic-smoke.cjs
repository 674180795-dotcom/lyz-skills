#!/usr/bin/env node
"use strict";
// Runs the bundled inline JS against a tiny DOM model; this does not test rendering.
const assert = require("assert");
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const root = path.resolve(__dirname, "..");
const skill = fs.readFileSync(path.join(root, "SKILL.md"), "utf8");
const template = skill.match(/```html\n([\s\S]*?)\n```/)[1];
const example = fs.readFileSync(path.join(root, "examples/compound-growth.html"), "utf8");

function load(html) {
  const elements = new Map();
  const ids = [...html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g)];
  for (const match of ids) {
    const tag = match[0];
    const value = tag.match(/\bvalue="([^"]*)"/);
    elements.set(match[1], {
      value: value ? value[1] : "", textContent: "", hidden: /\bhidden\b/.test(tag),
      listeners: {}, attrs: {},
      addEventListener(name, callback) { this.listeners[name] = callback; },
      setAttribute(name, value) { this.attrs[name] = String(value); },
      focus() { this.focused = true; }
    });
  }
  const presetButtons = [...html.matchAll(/<button[^>]*data-rate="([^"]+)"[^>]*>/g)].map(m => ({
    dataset: { rate: m[1] }, listeners: {},
    addEventListener(name, callback) { this.listeners[name] = callback; }
  }));
  const document = {
    getElementById: id => { assert(elements.has(id), `missing ${id}`); return elements.get(id); },
    querySelectorAll: selector => selector === "[data-rate]" ? presetButtons : []
  };
  const js = html.match(/<script>([\s\S]*?)<\/script>/)[1];
  vm.runInNewContext(js, { document, requestAnimationFrame: callback => callback() }, { timeout: 1000 });
  return { elements, presets: presetButtons, get: id => elements.get(id) };
}

const t = load(template);
assert.equal(t.get("yv").textContent, "0.250");
assert(t.get("curve").attrs.d.startsWith("M"));
t.get("x").value = "0.8"; t.get("x").listeners.input();
assert.equal(t.get("yv").textContent, "0.640");
t.get("reset").onclick(); assert.equal(t.get("yv").textContent, "0.250");
t.get("start").onclick(); assert(t.get("learning").hidden && !t.get("quiz").hidden);

const e = load(example);
assert.equal(e.get("compoundResult").textContent, "429.98");
assert.equal(e.get("simpleResult").textContent, "260.00");
e.presets[0].listeners.click();
assert.equal(e.get("compoundResult").textContent, "100.00");
assert.equal(e.get("simpleResult").textContent, "100.00");
e.presets[2].listeners.click(); assert.equal(e.get("compoundResult").textContent, "1475.79");
e.get("reset").listeners.click(); assert.equal(e.get("compoundResult").textContent, "429.98");
e.get("startExam").listeners.click();
assert(e.get("learning").hidden && !e.get("questions").hidden);
assert.equal(e.get("error").hidden, true);
console.log(JSON.stringify({ ok: true, template: "default/input/reset/quiz", example: "default/extremes/reset/quiz" }));
