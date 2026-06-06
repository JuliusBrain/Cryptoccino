source "https://rubygems.org"

# Local-preview-only. GitHub Pages still builds with Jekyll 3.10 + the
# official plugin allowlist, but Jekyll 3.x doesn't load cleanly on
# modern Ruby. Jekyll 4 is close enough for layout / template / CSS
# previews; CI builds production via Pages so this never reaches users.
gem "jekyll", "~> 4.4"
gem "webrick"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.17"
  gem "jekyll-sitemap", "~> 1.4"
end
