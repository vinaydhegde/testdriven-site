---
layout: blog
title: Caleb Pollman
permalink: authors/pollman
type: author
---

<hr><br>

<img src="/assets/img/authors/pollman.jpg" style="max-width:200px;border-radius:50%" alt="caleb pollman">

Caleb is a software developer with a background in fine art and design. He's excited to learn new things and is most comfortable in challenging environments. In his free time he creates art and hangs out with random cats.

### Links

- [GitHub](https://github.com/calebpollman)
- [LinkedIn](https://www.linkedin.com/in/calebpollman/)

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
