(function(){
  'use strict';
  function ready(fn){ document.readyState==='loading'?document.addEventListener('DOMContentLoaded',fn):fn(); }

  /* ── Carregar Leaflet CSS/JS dinamicamente ──────────────── */
  function loadLeaflet(callback){
    if(window.L){ callback(); return; }
    var css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(css);
    var js = document.createElement('script');
    js.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    js.onload = callback;
    document.head.appendChild(js);
  }

  ready(function(){
    /* ── Referências ─────────────────────────────────────── */
    var rotaField      = document.getElementById('id_rota');
    var clienteField   = document.getElementById('id_cliente');
    if(!rotaField || !clienteField) return;

    var rotaOrigem = '';
    var leafletMap = null;

    /* ── Coletar todos os IDs de clientes do form ────────── */
    function getClienteIds(){
      var ids = [];
      if(clienteField.value) ids.push(clienteField.value);
      for(var i=0; i<20; i++){
        var f = document.getElementById('id_clientes_adicionais-'+i+'-cliente');
        if(!f) break;
        if(f.value) ids.push(f.value);
      }
      var seen = {};
      return ids.filter(function(id){
        if(seen[id]) return false;
        seen[id] = true;
        return true;
      });
    }

    /* ── Botão Calcular ──────────────────────────────────── */
    var clientesGroup = document.getElementById('clientes_adicionais-group');
    if(!clientesGroup) return;

    var calcWrap = document.createElement('div');
    calcWrap.style.cssText = 'text-align:center;padding:18px 0;';
    calcWrap.innerHTML =
      '<button type="button" id="btn-calc-rota-carga" style="'
      +'background:linear-gradient(135deg,#00d9a6,#00b894);color:#070d1a;'
      +'border:none;border-radius:12px;padding:14px 36px;font-size:1rem;font-weight:800;'
      +'cursor:pointer;transition:all .2s;letter-spacing:.04em;'
      +'box-shadow:0 4px 18px rgba(0,217,166,.3);">'
      +'🚛 Calcular Melhor Rota de Entrega</button>'
      +'<div id="carga-calc-status" style="margin-top:10px;font-size:.8rem;color:#8892a4;display:none;"></div>';

    clientesGroup.parentNode.insertBefore(calcWrap, clientesGroup.nextSibling);

    var calcBtn = document.getElementById('btn-calc-rota-carga');
    calcBtn.addEventListener('mouseenter',function(){
      calcBtn.style.transform='translateY(-2px)';
      calcBtn.style.boxShadow='0 6px 24px rgba(0,217,166,.4)';
    });
    calcBtn.addEventListener('mouseleave',function(){
      calcBtn.style.transform='';
      calcBtn.style.boxShadow='0 4px 18px rgba(0,217,166,.3)';
    });
    calcBtn.addEventListener('click', function(){ calcularRota(); });

    /* ── Container resultado ─────────────────────────────── */
    var container = document.createElement('div');
    container.id = 'carga-rota-container';
    container.style.cssText = 'display:none;margin:20px 0;'
      +'background:linear-gradient(145deg,#0d1929 40%,#0f2235);'
      +'border:1px solid rgba(0,217,166,.18);border-radius:16px;overflow:hidden;'
      +'box-shadow:0 6px 30px rgba(0,0,0,.3);';

    container.innerHTML =
      '<div style="padding:16px 22px;display:flex;align-items:center;gap:10px;'
      +'border-bottom:1px solid rgba(0,217,166,.1);">'
      +'<span style="font-size:1.5rem;">🗺️</span>'
      +'<span style="font-size:.95rem;font-weight:800;color:#00d9a6;letter-spacing:.04em;">ROTA DAS ENTREGAS</span>'
      +'<span style="flex:1"></span>'
      +'<span id="carga-rota-spinner" style="font-size:.72rem;color:#f59e0b;font-weight:600;display:none;">⏳ Calculando...</span>'
      +'<a id="carga-rota-gmaps" href="#" target="_blank" style="background:rgba(59,130,246,.12);color:#3b82f6;'
      +'border:1px solid rgba(59,130,246,.3);border-radius:7px;padding:5px 14px;font-size:.7rem;font-weight:700;'
      +'text-decoration:none;transition:all .15s;display:none;"'
      +' onmouseover="this.style.background=\'#3b82f6\';this.style.color=\'#fff\'"'
      +' onmouseout="this.style.background=\'rgba(59,130,246,.12)\';this.style.color=\'#3b82f6\'">🔗 Abrir no Google Maps</a>'
      +'</div>'
      +'<div style="display:grid;grid-template-columns:1fr 320px;min-height:480px;">'
      +'<div id="carga-rota-map" style="min-height:480px;width:100%;height:100%;background:#070d1a;"></div>'
      +'<div style="padding:16px;display:flex;flex-direction:column;gap:12px;'
      +'border-left:1px solid rgba(0,217,166,.1);overflow-y:auto;">'

      +'<div style="background:#070d1a;border:1px solid rgba(0,217,166,.12);border-radius:12px;padding:16px;text-align:center;">'
      +'<div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.12em;color:#8892a4;margin-bottom:6px;">Distância Total</div>'
      +'<div id="carga-rota-dist" style="font-size:2rem;font-weight:800;color:#00d9a6;">—</div>'
      +'<div style="font-size:.65rem;color:#8892a4;">KM</div>'
      +'</div>'

      +'<div style="background:#070d1a;border:1px solid rgba(245,158,11,.12);border-radius:12px;padding:16px;text-align:center;">'
      +'<div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.12em;color:#8892a4;margin-bottom:6px;">⏱️ Tempo Estimado</div>'
      +'<div id="carga-rota-tempo" style="font-size:2rem;font-weight:800;color:#f59e0b;">—</div>'
      +'<div style="font-size:.6rem;color:#8892a4;">Tempo total da rota com paradas</div>'
      +'</div>'

      +'<div style="background:#070d1a;border:1px solid rgba(59,130,246,.12);border-radius:12px;padding:16px;text-align:center;">'
      +'<div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.12em;color:#8892a4;margin-bottom:6px;">🚛 Trajeto</div>'
      +'<div id="carga-rota-trajeto" style="font-size:.85rem;font-weight:700;color:#3b82f6;line-height:1.6;">—</div>'
      +'</div>'

      +'<div style="background:#070d1a;border:1px solid rgba(16,185,129,.12);border-radius:12px;padding:16px;text-align:center;">'
      +'<div style="font-size:.6rem;text-transform:uppercase;letter-spacing:.12em;color:#8892a4;margin-bottom:6px;">📋 Melhor Ordem de Entrega</div>'
      +'<div id="carga-rota-ordem" style="font-size:.85rem;font-weight:700;color:#10b981;line-height:1.8;">—</div>'
      +'</div>'

      +'</div></div>'

      +'<div style="padding:8px 22px;font-size:.58rem;color:#8892a4;text-align:center;'
      +'border-top:1px solid rgba(0,217,166,.06);">'
      +'⚠️ A ordem de entrega é otimizada automaticamente para o menor percurso total.'
      +'</div>';

    calcWrap.parentNode.insertBefore(container, calcWrap.nextSibling);

    /* ── Google Maps link externo ─────────────────────────── */
    function buildGmapsUrl(pontos){
      if(pontos.length < 2) return '';
      var parts = pontos.map(function(p){ return p.lat+','+p.lng; });
      return 'https://www.google.com/maps/dir/' + parts.join('/') + '/';
    }

    /* ── Desenhar mapa Leaflet ───────────────────────────── */
    function renderMap(pontos, rotaCoords){
      var mapDiv = document.getElementById('carga-rota-map');
      if(leafletMap){ leafletMap.remove(); leafletMap = null; }

      leafletMap = L.map(mapDiv, {zoomControl:true, attributionControl:false});
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
        maxZoom:18
      }).addTo(leafletMap);

      // Polyline da rota (coords vêm como [lng, lat] do GeoJSON)
      if(rotaCoords && rotaCoords.length > 1){
        var latlngs = rotaCoords.map(function(c){ return [c[1], c[0]]; });
        L.polyline(latlngs, {color:'#00d9a6', weight:5, opacity:0.9}).addTo(leafletMap);
      }

      // Marcadores
      var bounds = [];
      pontos.forEach(function(p, idx){
        var isOrigin = idx === 0;
        var color = isOrigin ? '#00d9a6' : '#3b82f6';
        var label = isOrigin ? '🏭' : (idx).toString();
        var icon = L.divIcon({
          className:'',
          html:'<div style="background:'+color+';color:#070d1a;border-radius:50%;width:28px;height:28px;'
            +'display:flex;align-items:center;justify-content:center;font-size:'+(isOrigin?'16px':'13px')+';font-weight:800;'
            +'border:2px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.4);">'+label+'</div>',
          iconSize:[28,28],
          iconAnchor:[14,14]
        });
        L.marker([p.lat, p.lng], {icon:icon})
          .bindPopup('<b>'+(isOrigin?'Origem: ':'Parada '+idx+': ')+p.nome+'</b>')
          .addTo(leafletMap);
        bounds.push([p.lat, p.lng]);
      });

      if(bounds.length > 0){
        leafletMap.fitBounds(bounds, {padding:[30,30]});
      }
      // Forçar recalculo de tamanho após container visível
      setTimeout(function(){
        leafletMap.invalidateSize();
        if(bounds.length > 0) leafletMap.fitBounds(bounds, {padding:[30,30]});
      }, 300);
    }

    /* ── Buscar origem da rota selecionada ────────────────── */
    function fetchRotaOrigem(callback){
      var rotaId = rotaField.value;
      if(!rotaId){ rotaOrigem = ''; callback(); return; }
      fetch('/operacao/api/rota/'+rotaId+'/info/')
        .then(function(r){ return r.json(); })
        .then(function(data){
          rotaOrigem = data.origem || '';
          callback();
        })
        .catch(function(){ rotaOrigem = ''; callback(); });
    }

    /* ── Calcular rota ───────────────────────────────────── */
    function calcularRota(){
      if(!rotaField.value){
        showStatus('⚠️ Selecione a rota primeiro.','#f59e0b');
        return;
      }

      var clienteIds = getClienteIds();
      if(!clienteIds.length){
        showStatus('⚠️ Selecione ao menos um cliente.','#f59e0b');
        return;
      }

      var spinner = document.getElementById('carga-rota-spinner');
      spinner.style.display = 'inline';
      calcBtn.style.opacity = '.5';
      calcBtn.style.pointerEvents = 'none';
      showStatus('⏳ Buscando dados da rota e calculando...','#f59e0b');

      fetchRotaOrigem(function(){
        if(!rotaOrigem){
          spinner.style.display = 'none';
          calcBtn.style.opacity = '1';
          calcBtn.style.pointerEvents = '';
          showStatus('⚠️ Não foi possível obter a origem da rota.','#f59e0b');
          return;
        }

        var params = new URLSearchParams();
        params.set('origem', rotaOrigem);
        clienteIds.forEach(function(id){ params.append('parada_id', id); });

        fetch('/operacao/api/distancia/?'+params.toString())
          .then(function(r){ return r.json(); })
          .then(function(data){
            spinner.style.display = 'none';
            calcBtn.style.opacity = '1';
            calcBtn.style.pointerEvents = '';

            if(data.error){
              showStatus('❌ '+data.error,'#ef4444');
              return;
            }

            showStatus('✅ Rota otimizada! '+data.distancia_km+' km — melhor ordem de entrega calculada.','#10b981');

            // Montar pontos na ordem otimizada
            var pontos = [{nome:data.origem_nome||rotaOrigem, lat:data.origem_lat, lng:data.origem_lng}];
            if(data.ordem_entrega){
              data.ordem_entrega.forEach(function(e){
                if(e.lat && e.lng) pontos.push({nome:e.nome, lat:e.lat, lng:e.lng});
              });
            }
            if(pontos.length < 2){
              pontos.push({nome:data.destino_nome||'Destino', lat:data.destino_lat, lng:data.destino_lng});
            }

            // Mostrar container e renderizar mapa Leaflet
            container.style.display = 'block';
            loadLeaflet(function(){
              setTimeout(function(){ renderMap(pontos, data.rota_coords); }, 100);
            });

            // Link externo Google Maps
            var gmBtn = document.getElementById('carga-rota-gmaps');
            gmBtn.href = buildGmapsUrl(pontos);
            gmBtn.style.display = 'inline-block';

            // Cards
            document.getElementById('carga-rota-dist').textContent =
              Number(data.distancia_km).toLocaleString('pt-BR');
            var h=data.tempo_total_h, m_val=data.tempo_total_m;
            document.getElementById('carga-rota-tempo').textContent =
              h+'h '+(m_val<10?'0':'')+m_val+'min';

            var trajetoNomes = data.trajeto_nomes || [data.origem_nome||rotaOrigem];
            document.getElementById('carga-rota-trajeto').innerHTML = trajetoNomes.map(function(nome,idx){
              var prefix = idx===0 ? '🏭 ' : '🛢️ ';
              var color = idx===0 ? '#00d9a6' : '#3b82f6';
              return '<span style="color:'+color+';">'+prefix+nome+'</span>';
            }).join('<br><span style="font-size:.9rem;color:#8892a4;">⬇️</span><br>');

            var ordemEl = document.getElementById('carga-rota-ordem');
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

            container.style.animation = 'none';
            container.offsetHeight;
            container.style.animation = 'cargaFadeSlide .4s ease-out';
          })
          .catch(function(){
            spinner.style.display = 'none';
            calcBtn.style.opacity = '1';
            calcBtn.style.pointerEvents = '';
            showStatus('❌ Erro ao calcular rota. Tente novamente.','#ef4444');
          });
      });
    }

    function showStatus(msg, color){
      var el = document.getElementById('carga-calc-status');
      el.style.display = 'block';
      el.style.color = color;
      el.textContent = msg;
    }

    var style = document.createElement('style');
    style.textContent = '@keyframes cargaFadeSlide{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}'
      +'#carga-rota-map .leaflet-tile-pane{filter:saturate(.3) brightness(.7);}';
    document.head.appendChild(style);
  });
})();
