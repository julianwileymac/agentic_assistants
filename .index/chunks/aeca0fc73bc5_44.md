# Chunk: aeca0fc73bc5_44

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 2862-2924
- chunk: 45/45

```
et i = 0; i < modules.length; i++) {
      let mod = modules[i], index = this.modules.indexOf(mod)
      if (index < j && index > -1) { // Ordering conflict
        this.modules.splice(index, 1)
        j--
        index = -1
      }
      if (index == -1) {
        this.modules.splice(j++, 0, mod)
        if (sheet) for (let k = 0; k < mod.rules.length; k++)
          sheet.insertRule(mod.rules[k], pos++)
      } else {
        while (j < index) pos += this.modules[j++].rules.length
        pos += mod.rules.length
        j++
      }
    }

    if (!sheet) {
      let text = ""
      for (let i = 0; i < this.modules.length; i++)
        text += this.modules[i].getRules() + "\n"
      this.styleTag.textContent = text
    }
  }

  setNonce(nonce) {
    if (this.styleTag && this.styleTag.getAttribute("nonce") != nonce)
      this.styleTag.setAttribute("nonce", nonce)
  }
}

// Style::Object<union<Style,string>>
//
// A style is an object that, in the simple case, maps CSS property
// names to strings holding their values, as in `{color: "red",
// fontWeight: "bold"}`. The property names can be given in
// camel-case—the library will insert a dash before capital letters
// when converting them to CSS.
//
// If you include an underscore in a property name, it and everything
// after it will be removed from the output, which can be useful when
// providing a property multiple times, for browser compatibility
// reasons.
//
// A property in a style object can also be a sub-selector, which
// extends the current context to add a pseudo-selector or a child
// selector. Such a property should contain a `&` character, which
// will be replaced by the current selector. For example `{"&:before":
// {content: '"hi"'}}`. Sub-selectors and regular properties can
// freely be mixed in a given object. Any property containing a `&` is
// assumed to be a sub-selector.
//
// Finally, a property can specify an @-block to be wrapped around the
// styles defined inside the object that's the property's value. For
// example to create a media query you can do `{"@media screen and
// (min-width: 400px)": {...}}`.


/***/ })

}]);
//# sourceMappingURL=1584.5e136a9d8643093bc7e9.js.map?v=5e136a9d8643093bc7e9
```
