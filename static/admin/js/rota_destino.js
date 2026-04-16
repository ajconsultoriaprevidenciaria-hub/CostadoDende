(function(){
  'use strict';
  function ready(fn){ document.readyState==='loading'?document.addEventListener('DOMContentLoaded',fn):fn(); }

  ready(function(){
    var destinoField = document.getElementById('id_destino');
    var origemField  = document.getElementById('id_origem');
    var distField    = document.getElementById('id_distancia_km');
    var tempoField   = document.getElementById('id_tempo_total_min');
    var latField     = document.getElementById('id_destino_lat');
    var lngField     = document.getElementById('id_destino_lng');
    var paradaFields = [1,2,3,4,5,6,7].map(function(i){ return document.getElementById('id_parada_' + i); }).filter(Boolean);
    if(!destinoField) return;

    var ORIGENS = {
      'Candeias/BA':                  {lat:-12.67218, lng:-38.54737},
      'São Francisco do Conde/BA':    {lat:-12.62836, lng:-38.67952},
      'Suape/PE':                     {lat:-8.39356,  lng:-35.06017}
    };

    /* ═══════════════════════════════════════════════════════════
       INJETAR MAPA + PAINEL DEPOIS DOS FIELDSETS
       ═══════════════════════════════════════════════════════════ */
    var container = document.createElement('div');
    container.id = 'rota-container';
    container.style.cssText = 'display:none;margin:20px 0;'
      +'background:linear-gradient(145deg,#0d1929 40%,#0f2235);'
      +'border:1px solid rgba(0,217,166,.18);border-radius:16px;overflow:hidden;'
      +'box-shadow:0 6px 30px rgba(0,0,0,.3);';

    container.innerHTML =
      /* Header */
      '<div style="padding:16px 22px;display:flex;align-items:center;gap:10px;'
      +'border-bottom:1px solid rgba(0,217,166,.1);">'
      +'<span style="font-size:1.5rem;">🗺️</span>'
      +'<span style="font-size:.95rem;font-weight:800;color:#00d9a6;letter-spacing:.04em;">MAPA DA ROTA</span>'
      +'<span style="flex:1"></span>'
      +'<span id="rota-spinner" style="font-size:.72rem;color:#f59e0b;font-weight:600;display:none;">⏳ Calculando...</span>'
      +'<a id="rota-gmaps" href="#" target="_blank" style="background:rgba(59,130,246,.12);color:#3b82f6;'
      +'border:1px solid rgba(59,130,246,.3);border-radius:7px;padding:5px 14px;font-size:.7rem;font-weight:700;'
      +'text-decoration:none;transition:all .15s;display:none;"'
      +' onmouseover="this.style.background=\'#3b82f6\';this.style.color=\'#fff\'"'
      +' onmouseout="this.style.background=\'rgba(59,130,246,.12)\';this.style.color=\'#3b82f6\'">🗺️ Google Maps</a>'
      +'</div>'
      /* Layout: mapa + cards lado a lado */
      +'<div style="display:grid;grid-template-columns:1fr 320px;min-height:420px;">'
      /* Mapa */
      +'<div id="rota-map" style="min-height:420px;background:#070d1a;"></div>'
      /* Cards lateral */
      +'<div id="rota-cards" style="padding:16px;display:flex;flex-direction:column;gap:12px;'
      +'border-left:1px solid rgba(0,217,166,.1);overflow-y:auto;">'

      /* Card Distância */
      +'<div style="background:#070d1a;border:1px solid rgba(0,217,166,.12);border-radius:12px;padding:16px;text-align:center;">'
      +'<div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.12em;color:#8892a4;margin-bottom:6px;">Distância Rodoviária</div>'
      +'<div id="rota-dist" style="font-size:2rem;font-weight:800;color:#00d9a6;">—</div>'
      +'<div style="font-size:.65rem;color:#8892a4;">KM</div>'
      +'</div>'

      /* Card Tempo */
      +'<div style="background:#070d1a;border:1px solid rgba(245,158,11,.12);border-radius:12px;padding:16px;text-align:center;">'
      +'<div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.12em;color:#8892a4;margin-bottom:6px;">⏱️ Tempo Estimado</div>'
      +'<div id="rota-tempo" style="font-size:2rem;font-weight:800;color:#f59e0b;">—</div>'
  		+'<div style="font-size:.6rem;color:#8892a4;">Tempo total da rota com paradas</div>'
      +'</div>'

      /* Card Trajeto */
      +'<div style="background:#070d1a;border:1px solid rgba(59,130,246,.12);border-radius:12px;padding:16px;text-align:center;">'
      +'<div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.12em;color:#8892a4;margin-bottom:6px;">🚛 Trajeto</div>'
      +'<div id="rota-trajeto" style="font-size:.85rem;font-weight:700;color:#3b82f6;line-height:1.6;">—</div>'
      +'</div>'

      /* Card Ordem de Entrega */
      +'<div style="background:#070d1a;border:1px solid rgba(16,185,129,.12);border-radius:12px;padding:16px;text-align:center;">'
      +'<div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.12em;color:#8892a4;margin-bottom:6px;">📋 Ordem de Entrega</div>'
      +'<div id="rota-ordem" style="font-size:.85rem;font-weight:700;color:#10b981;line-height:1.8;">—</div>'
      +'</div>'

      /* Instrução */
      +'<div style="font-size:.6rem;color:#8892a4;text-align:center;line-height:1.5;padding:8px;">'
      +'📌 <b>Clique no mapa</b> para alfinetar o destino exato.<br>'
      +'O alfinete é <b>arrastável</b> — mova para ajustar.'
      +'</div>'

      +'</div></div>'

      /* Nota rodapé */
      +'<div style="padding:8px 22px;font-size:.58rem;color:#8892a4;text-align:center;'
      +'border-top:1px solid rgba(0,217,166,.06);">'
      +'⚠️ Rota calculada via OpenStreetMap/OSRM. Variação de ±5% em relação ao Google Maps é normal. '
      +'O campo Distância KM é editável para ajuste manual.'
      +'</div>';

    var fieldsets = document.querySelectorAll('#content-main fieldset');
    if(fieldsets.length){
      fieldsets[fieldsets.length-1].parentNode.insertBefore(container, fieldsets[fieldsets.length-1].nextSibling);
    }

    /* ═══════════════════════════════════════════════════════════
       INICIALIZAR MAPA LEAFLET
       ═══════════════════════════════════════════════════════════ */
    var map = null, marker = null, routeLine = null, originMarker = null;

    function initMap(){
      if(map) return;
      map = L.map('rota-map',{
        zoomControl: true,
        scrollWheelZoom: true
      }).setView([-13.0, -38.5], 6);

      // Tile dark theme
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{
        attribution:'© OpenStreetMap © CARTO',
        maxZoom:18
      }).addTo(map);

      // Clique no mapa = alfinetar destino
      map.on('click', function(e){
        setDestinationMarker(e.latlng.lat, e.latlng.lng);
        // Reverse geocode para preencher nome
        fetch('/operacao/api/reverse-geocode/?lat='+e.latlng.lat+'&lng='+e.latlng.lng)
          .then(function(r){ return r.json(); })
          .then(function(data){
            if(data.nome) destinoField.value = data.nome;
            calcularDistancia(e.latlng.lat, e.latlng.lng);
          })
          .catch(function(){ calcularDistancia(e.latlng.lat, e.latlng.lng); });
      });

      // Resize fix
      setTimeout(function(){ map.invalidateSize(); }, 200);
    }

    // Ícones customizados
    var truckIcon = L.divIcon({
      html:'<div style="font-size:24px;text-shadow:0 2px 8px rgba(0,0,0,.5);">🚛</div>',
      iconSize:[30,30], iconAnchor:[15,15], className:''
    });
    var pinIcon = L.divIcon({
      html:'<div style="font-size:28px;text-shadow:0 2px 8px rgba(0,0,0,.6);filter:drop-shadow(0 0 6px #ef4444);">📍</div>',
      iconSize:[30,36], iconAnchor:[15,36], className:''
    });

    function setDestinationMarker(lat, lng){
      if(marker){
        marker.setLatLng([lat, lng]);
      } else {
        marker = L.marker([lat, lng],{
          icon: pinIcon,
          draggable: true
        }).addTo(map);
        // Ao arrastar, recalcular
        marker.on('dragend', function(){
          var pos = marker.getLatLng();
          fetch('/operacao/api/reverse-geocode/?lat='+pos.lat+'&lng='+pos.lng)
            .then(function(r){ return r.json(); })
            .then(function(data){
              if(data.nome) destinoField.value = data.nome;
              calcularDistancia(pos.lat, pos.lng);
            })
            .catch(function(){ calcularDistancia(pos.lat, pos.lng); });
        });
      }
    }

    function setOriginMarker(lat, lng){
      if(originMarker){
        originMarker.setLatLng([lat, lng]);
      } else {
        originMarker = L.marker([lat, lng],{icon: truckIcon}).addTo(map);
      }
    }

    function drawRoute(coords, oLat, oLng, dLat, dLng){
      if(routeLine) map.removeLayer(routeLine);
      // Coords do OSRM vêm como [lng, lat]
      var latlngs = coords.map(function(c){ return [c[1], c[0]]; });
      routeLine = L.polyline(latlngs,{
        color:'#00d9a6', weight:4, opacity:.8,
        dashArray:'8 4'
      }).addTo(map);
      setOriginMarker(oLat, oLng);
      setDestinationMarker(dLat, dLng);
      // Fit bounds
      var group = L.featureGroup([routeLine, originMarker, marker]);
      map.fitBounds(group.getBounds().pad(0.1));
    }

    /* ═══════════════════════════════════════════════════════════
       AUTOCOMPLETE DROPDOWN
       ═══════════════════════════════════════════════════════════ */
    var wrap = destinoField.parentNode;
    wrap.style.position = 'relative';
    var dd = document.createElement('div');
    dd.id = 'destino-dropdown';
    dd.style.cssText = 'position:absolute;top:100%;left:0;right:0;z-index:9999;'
      +'background:#0d1929;border:1px solid rgba(0,217,166,.25);border-radius:8px;'
      +'max-height:260px;overflow-y:auto;display:none;margin-top:2px;'
      +'box-shadow:0 8px 30px rgba(0,0,0,.4);';
    wrap.appendChild(dd);

    var timer = null;
    destinoField.setAttribute('autocomplete','off');
    destinoField.setAttribute('placeholder','Digite o nome da cidade...');
    destinoField.addEventListener('input', function(){
      clearTimeout(timer);
      var q = destinoField.value.trim();
      if(q.length < 2){ dd.style.display='none'; return; }
      timer = setTimeout(function(){ buscarCidades(q); }, 350);
    });

    function buscarCidades(q){
      fetch('/operacao/api/cidades/?q=' + encodeURIComponent(q))
        .then(function(r){ return r.json(); })
        .then(function(data){
          dd.innerHTML = '';
          if(!data.length){ dd.style.display='none'; return; }
          data.forEach(function(c){
            var item = document.createElement('div');
            item.innerHTML = '<span style="color:#00d9a6;margin-right:6px;">📍</span>' + c.nome;
            item.style.cssText = 'padding:9px 14px;cursor:pointer;font-size:.8rem;color:#dde6f0;'
              +'border-bottom:1px solid rgba(0,217,166,.06);transition:all .12s;';
            item.addEventListener('mouseenter',function(){
              item.style.background='rgba(0,217,166,.08)';item.style.paddingLeft='18px';
            });
            item.addEventListener('mouseleave',function(){
              item.style.background='transparent';item.style.paddingLeft='14px';
            });
            item.addEventListener('click',function(){
              destinoField.value = c.nome;
              dd.style.display = 'none';
              calcularDistancia();
            });
            dd.appendChild(item);
          });
          dd.style.display = 'block';
        })
        .catch(function(){ dd.style.display='none'; });
    }

    document.addEventListener('click', function(e){
      if(!wrap.contains(e.target)) dd.style.display='none';
    });

    /* ═══════════════════════════════════════════════════════════
       BOTÃO CALCULAR
       ═══════════════════════════════════════════════════════════ */
    var calcBtn = document.createElement('a');
    calcBtn.href = '#';
    calcBtn.innerHTML = '🚛 Calcular Rota';
    calcBtn.style.cssText = 'display:inline-block;margin-top:8px;'
      +'background:linear-gradient(135deg,#00d9a6,#00b894);color:#070d1a;'
      +'border-radius:8px;padding:7px 18px;font-size:.75rem;font-weight:800;'
      +'text-decoration:none;transition:all .18s;'
      +'box-shadow:0 2px 10px rgba(0,217,166,.25);';
    calcBtn.addEventListener('mouseenter',function(){
      calcBtn.style.transform='translateY(-1px)';
      calcBtn.style.boxShadow='0 4px 16px rgba(0,217,166,.35)';
    });
    calcBtn.addEventListener('mouseleave',function(){
      calcBtn.style.transform='';
      calcBtn.style.boxShadow='0 2px 10px rgba(0,217,166,.25)';
    });
    calcBtn.addEventListener('click', function(e){ e.preventDefault(); calcularDistancia(); });
    wrap.appendChild(document.createElement('br'));
    wrap.appendChild(calcBtn);

    /* ═══════════════════════════════════════════════════════════
       CALCULAR DISTÂNCIA + ATUALIZAR MAPA + PAINEL
       ═══════════════════════════════════════════════════════════ */
    function calcularDistancia(clickLat, clickLng){
      var origem = origemField ? origemField.value : '';
      var destino = destinoField.value.trim();
      var paradaIds = paradaFields.map(function(f){ return (f.value || '').trim(); }).filter(function(v){ return v && v !== ''; });
      if(!origem) return;
      if(!destino && !clickLat && !paradaIds.length) return;

      var spinner = document.getElementById('rota-spinner');
      spinner.style.display = 'inline';
      calcBtn.style.opacity = '.5';
      calcBtn.style.pointerEvents = 'none';
      if(distField) distField.value = '...';

      var params = new URLSearchParams();
      params.set('origem', origem);
      if(destino) params.set('destino', destino);
      paradaIds.forEach(function(id){ params.append('parada_id', id); });
      if(clickLat && clickLng){
        params.set('lat', clickLat);
        params.set('lng', clickLng);
      }
      var url = '/operacao/api/distancia/?' + params.toString();

      fetch(url)
        .then(function(r){ return r.json(); })
        .then(function(data){
          spinner.style.display = 'none';
          calcBtn.style.opacity = '1';
          calcBtn.style.pointerEvents = '';

          if(data.error){
            if(distField) distField.value = '';
            return;
          }

          // Campos do form
          if(distField) distField.value = data.distancia_km;
          if(tempoField) tempoField.value = data.tempo_total_min;
          if(latField)  latField.value  = data.destino_lat;
          if(lngField)  lngField.value  = data.destino_lng;

          // Nome auto
          var nomeField = document.getElementById('id_nome');
          if(nomeField && !nomeField.value){
            var on = (data.origem_nome||origem).split('/')[0];
            var dn = (data.destino_nome||destino).split('/')[0];
            nomeField.value = on + ' x ' + dn;
          }

          // Mostrar container + mapa
          container.style.display = 'block';
          initMap();
          setTimeout(function(){ map.invalidateSize(); }, 100);

          // Desenhar rota
          if(data.rota_coords){
            drawRoute(data.rota_coords, data.origem_lat, data.origem_lng, data.destino_lat, data.destino_lng);
          }

          // Cards
          document.getElementById('rota-dist').textContent =
            Number(data.distancia_km).toLocaleString('pt-BR');
          var h = data.tempo_total_h, m = data.tempo_total_m;
          document.getElementById('rota-tempo').textContent =
            h + 'h ' + (m<10?'0':'') + m + 'min';
          var trajetoNomes = data.trajeto_nomes || [data.origem_nome || origem, data.destino_nome || destino];
          document.getElementById('rota-trajeto').innerHTML = trajetoNomes.map(function(nome, idx){
            var prefix = idx === 0 ? '🏭 ' : (idx === trajetoNomes.length - 1 ? '📍 ' : '🛑 ');
            var color = idx === 0 ? '#00d9a6' : (idx === trajetoNomes.length - 1 ? '#f59e0b' : '#3b82f6');
            return '<span style="color:'+color+';">' + prefix + nome + '</span>';
          }).join('<br><span style="font-size:.9rem;color:#8892a4;">⬇️</span><br>');

          // Google Maps link
          var gmBtn = document.getElementById('rota-gmaps');
          gmBtn.href = data.gmaps_url;
          gmBtn.style.display = 'inline-block';

          // Ordem de entrega
          var ordemEl = document.getElementById('rota-ordem');
          if(data.ordem_entrega && data.ordem_entrega.length > 0){
            ordemEl.innerHTML = data.ordem_entrega.map(function(item){
              return '<div style="display:flex;align-items:center;gap:8px;justify-content:center;">'
                +'<span style="background:#10b981;color:#070d1a;border-radius:50%;width:22px;height:22px;'
                +'display:inline-flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:800;">'
                +item.ordem+'</span>'
                +'<span>'+item.nome+'</span>'
                +'</div>';
            }).join('');
          } else {
            ordemEl.innerHTML = '—';
          }

          // Animação
          container.style.animation = 'none';
          container.offsetHeight;
          container.style.animation = 'fadeSlide .4s ease-out';
        })
        .catch(function(){
          spinner.style.display = 'none';
          calcBtn.style.opacity = '1';
          calcBtn.style.pointerEvents = '';
          if(distField) distField.value = '';
        });
    }

    // Recalcular ao mudar origem
    if(origemField){
      origemField.addEventListener('change', function(){
        if(destinoField.value.trim()) calcularDistancia();
      });
    }

    paradaFields.forEach(function(field){
      field.addEventListener('change', function(){
        if(destinoField.value.trim() || paradaFields.some(function(f){ return f.value; })) calcularDistancia();
      });
    });
    // Select2 (autocomplete_fields) dispara change via jQuery
    if(window.django && window.django.jQuery){
      paradaFields.forEach(function(field){
        django.jQuery(field).on('change', function(){
          if(destinoField.value.trim() || paradaFields.some(function(f){ return f.value; })) calcularDistancia();
        });
      });
    }

    // Se já tem lat/lng (edição), mostrar mapa
    if(latField && lngField && latField.value && lngField.value){
      container.style.display = 'block';
      initMap();
      var o = ORIGENS[origemField ? origemField.value : ''];
      if(o){
        setOriginMarker(o.lat, o.lng);
      }
      setDestinationMarker(parseFloat(latField.value), parseFloat(lngField.value));
      if(marker && originMarker){
        map.fitBounds(L.featureGroup([originMarker, marker]).getBounds().pad(0.2));
      }
    }

    // Animação CSS
    var style = document.createElement('style');
    style.textContent = '@keyframes fadeSlide{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}';
    document.head.appendChild(style);
  });
})();
