  function initDisclosureIcon() {
    var disclosure = document.querySelector("[data-disclosure]");
    if (!disclosure) {
      return;
    }
    var menuIcon = disclosure.querySelector("[data-icon-menu]");
    var closeIcon = disclosure.querySelector("[data-icon-close]");
    if (!menuIcon || !closeIcon) {
      return;
    }
    function sync() {
      menuIcon.hidden = disclosure.open;
      closeIcon.hidden = !disclosure.open;
    }
    disclosure.addEventListener("toggle", sync);
    sync();
  }
