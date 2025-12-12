"""
Wrapper entrypoint for Vercel.

This file exposes the FastAPI `app` variable. On some Vercel build/runtime
environments a vendored copy of packages (imported under `_vendor`) can
interfere with the installed site-packages and cause import-time errors
(for example Pydantic/FastAPI forward-ref evaluation failures). We try a
normal import first; if it fails we attempt a conservative workaround:
- remove any `_vendor` modules from `sys.modules`
- ensure site-packages paths are before the current working directory
- re-import `app.main`

This is a best-effort compatibility shim to improve reliability on Vercel.
"""

import sys
import importlib
import site


def _ensure_site_packages_first():
	# Prepend all site-packages paths so installed packages are preferred
	try:
		for p in site.getsitepackages():
			if p not in sys.path:
				sys.path.insert(0, p)
	except Exception:
		# site.getsitepackages() may not be available in some minimal envs
		pass


def _remove_vendor_modules():
	# Remove modules loaded under the _vendor package prefix so that
	# subsequent imports will load installed packages instead.
	to_remove = [name for name in sys.modules.keys() if name.startswith("_vendor")]
	for name in to_remove:
		try:
			del sys.modules[name]
		except KeyError:
			pass


try:
	from app.main import app
except Exception:
	# Attempt to recover from vendored-package conflicts by preferring
	# site-packages and clearing `_vendor` modules, then re-import.
	_remove_vendor_modules()
	_ensure_site_packages_first()
	# Try to import freshly
	try:
		importlib.invalidate_caches()
		mod = importlib.import_module("app.main")
		app = getattr(mod, "app")
	except Exception:
		# If this still fails, re-raise the original exception so Vercel logs it
		raise

