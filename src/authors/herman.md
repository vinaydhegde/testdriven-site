---
layout: blog
title: Michael Herman
permalink: authors/herman
type: author
---

<hr><br>

<img src="/assets/img/authors/herman.png" alt="michael herman">

Michael is a software engineer and educator who lives and works in the Denver/Boulder area. He is the co-founder/author of [Real Python](https://realpython.com/). Besides development, he enjoys building financial models, tech writing, content marketing, and teaching.

### Links

- [Twitter](https://twitter.com/mikeherman)
- [GitHub](https://github.com/mjhea0)
- [Personal Site](http://mherman.org/)

<div>
  <h3>Articles</h3>
  <ul>
    {% for post in site.posts %}
      {% if post.type == 'blog' and post.author == page.title %}
        <li><a href="{{site.url}}{{post.url}}">{{post.title}}</a></li>
      {% endif %}
    {% endfor %}
  </ul>
</div>
