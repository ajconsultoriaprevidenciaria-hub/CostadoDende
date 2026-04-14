(function(){
  'use strict';

  function ready(fn){ document.readyState==='loading'?document.addEventListener('DOMContentLoaded',fn):fn(); }

  ready(function(){
    /* ── Referências ─────────────────────────────────────── */
    var caminhaoSelect = document.querySelector('#id_caminhao');
    if(!caminhaoSelect) return;

    var produtos = [];      // [{id, nome}]
    var compartimentos = []; // [{id, numero, capacidade_litros}]
    var selecionados = {};   // {compId: produtoId}
    var lastCaminhaoVal = '';

    /* ── Container principal ─────────────────────────────── */
    var container = document.createElement('div');
    container.id = 'bocas-container';
    container.style.cssText =
      'display:none;margin:20px 0;background:linear-gradient(145deg,#0d1929 40%,#0f2235);'
      +'border:1px solid rgba(0,217,166,.18);border-radius:16px;overflow:hidden;'
      +'box-shadow:0 6px 30px rgba(0,0,0,.3);';
    container.innerHTML =
      '<div style="padding:16px 22px;display:flex;align-items:center;gap:10px;'
      +'border-bottom:1px solid rgba(0,217,166,.1);">'
      +'<span style="font-size:1.3rem;">🛢️</span>'
      +'<span style="font-size:.9rem;font-weight:800;color:#00d9a6;letter-spacing:.04em;">'
      +'SELECIONAR BOCAS &amp; PRODUTOS</span>'
      +'<span style="flex:1"></span>'
      +'<span id="bocas-resumo" style="font-size:.7rem;color:#8892a4;"></span>'
      +'</div>'
      +'<div style="display:grid;grid-template-columns:1fr 1fr;min-height:200px;">'
      /* Lado esquerdo: bocas */
      +'<div id="bocas-lista" style="padding:16px;border-right:1px solid rgba(0,217,166,.1);">'
      +'<div style="font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:#8892a4;'
      +'margin-bottom:12px;">📦 Bocas do Caminhão</div>'
      +'<div id="bocas-grid" style="display:flex;flex-wrap:wrap;gap:10px;"></div>'
      +'</div>'
      /* Lado direito: produtos */
      +'<div id="produtos-lista" style="padding:16px;">'
      +'<div style="font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:#8892a4;'
      +'margin-bottom:12px;">🧪 Selecione o Produto</div>'
      +'<div id="produtos-grid" style="display:flex;flex-direction:column;gap:6px;"></div>'
      +'<div id="produtos-placeholder" style="font-size:.75rem;color:#5a6478;padding:20px;text-align:center;">'
      +'👈 Clique em uma boca para ver os produtos</div>'
      +'</div>'
      +'</div>';

    // Inserir depois do campo caminhão
    var inlineGroup = document.querySelector('.inline-group');
    if(inlineGroup){
      inlineGroup.parentNode.insertBefore(container, inlineGroup);
    } else {
      var fieldsets = document.querySelectorAll('#content-main fieldset');
      if(fieldsets.length){
        fieldsets[fieldsets.length-1].parentNode.insertBefore(container, fieldsets[fieldsets.length-1].nextSibling);
      }
    }

    var bocaAtiva = null; // compartimento id atualmente selecionado

    /* ── Buscar Produtos (uma vez) ───────────────────────── */
    fetch('/operacao/api/produtos/')
      .then(function(r){ return r.json(); })
      .then(function(data){ produtos = data.produtos || []; })
      .catch(function(){});

    /* ── Quando Caminhão muda ────────────────────────────── */
    function onCaminhaoChange(){
      var val = caminhaoSelect.value;
      if(val === lastCaminhaoVal) return;
      lastCaminhaoVal = val;
      if(!val){
        container.style.display = 'none';
        compartimentos = [];
        selecionados = {};
        bocaAtiva = null;
        return;
      }
      fetch('/operacao/caminhao/' + val + '/compartimentos/')
        .then(function(r){ return r.json(); })
        .then(function(data){
          compartimentos = data.compartimentos || [];
          selecionados = {};
          bocaAtiva = null;
          if(compartimentos.length){
            container.style.display = 'block';
            container.style.animation = 'none';
            container.offsetHeight;
            container.style.animation = 'fadeSlide .4s ease-out';
            renderBocas();
            renderProdutos();
            updateResumo();
          } else {
            container.style.display = 'none';
          }
        })
        .catch(function(){ container.style.display = 'none'; });
    }

    caminhaoSelect.addEventListener('change', onCaminhaoChange);

    // Select2 (usado pelo autocomplete_fields do Django admin)
    function bindSelect2(){
      if(window.django && window.django.jQuery){
        django.jQuery('#id_caminhao').on('select2:select select2:clear change', onCaminhaoChange);
        return true;
      }
      return false;
    }
    if(!bindSelect2()){
      var s2tries = 0;
      var s2interval = setInterval(function(){
        if(bindSelect2() || ++s2tries > 30) clearInterval(s2interval);
      }, 200);
    }

    // Fallback: polling a cada 500ms
    setInterval(function(){
      if(caminhaoSelect.value !== lastCaminhaoVal) onCaminhaoChange();
    }, 500);

    /* ── Renderizar Bocas ────────────────────────────────── */
    function renderBocas(){
      var grid = document.getElementById('bocas-grid');
      grid.innerHTML = '';
      compartimentos.forEach(function(c){
        var card = document.createElement('div');
        card.dataset.compId = c.id;
        var sel = selecionados[c.id];
        var prodNome = sel ? getProdutoNome(sel) : null;

        card.style.cssText =
          'cursor:pointer;border-radius:12px;padding:14px 16px;min-width:110px;text-align:center;'
          +'transition:all .2s;position:relative;'
          + (sel
            ? 'background:rgba(0,217,166,.12);border:2px solid #00d9a6;'
            : (bocaAtiva===c.id
              ? 'background:rgba(59,130,246,.12);border:2px solid #3b82f6;'
              : 'background:#070d1a;border:2px solid rgba(0,217,166,.12);'));

        card.innerHTML =
          '<div style="font-size:1.6rem;margin-bottom:4px;">🛢️</div>'
          +'<div style="font-size:.82rem;font-weight:800;color:'+(sel?'#00d9a6':'#dde6f0')+';">'
          +'Boca '+c.numero+'</div>'
          +'<div style="font-size:.62rem;color:#8892a4;margin-top:2px;">'
          +Number(c.capacidade_litros).toLocaleString('pt-BR')+' L</div>'
          +(prodNome
            ? '<div style="margin-top:6px;font-size:.6rem;font-weight:700;color:#00d9a6;'
              +'background:rgba(0,217,166,.08);border-radius:6px;padding:3px 8px;">'+prodNome+'</div>'
              +'<div class="boca-remove" style="position:absolute;top:4px;right:6px;font-size:.65rem;'
              +'color:#ef4444;cursor:pointer;opacity:.7;" title="Remover">✕</div>'
            : '');

        card.addEventListener('click', function(e){
          if(e.target.classList.contains('boca-remove')){
            delete selecionados[c.id];
            bocaAtiva = null;
            renderBocas();
            renderProdutos();
            updateResumo();
            syncInlines();
            return;
          }
          bocaAtiva = c.id;
          renderBocas();
          renderProdutos();
        });

        card.addEventListener('mouseenter', function(){
          if(!selecionados[c.id] && bocaAtiva!==c.id)
            card.style.borderColor='rgba(0,217,166,.4)';
        });
        card.addEventListener('mouseleave', function(){
          if(!selecionados[c.id] && bocaAtiva!==c.id)
            card.style.borderColor='rgba(0,217,166,.12)';
        });

        grid.appendChild(card);
      });
    }

    /* ── Renderizar Produtos ─────────────────────────────── */
    function renderProdutos(){
      var grid = document.getElementById('produtos-grid');
      var placeholder = document.getElementById('produtos-placeholder');
      grid.innerHTML = '';

      if(!bocaAtiva){
        placeholder.style.display = 'block';
        return;
      }
      placeholder.style.display = 'none';

      var boca = compartimentos.find(function(c){ return c.id === bocaAtiva; });
      if(boca){
        var header = document.createElement('div');
        header.style.cssText = 'font-size:.75rem;color:#3b82f6;font-weight:700;margin-bottom:8px;';
        header.textContent = '🛢️ Boca ' + boca.numero + ' — selecione o produto:';
        grid.appendChild(header);
      }

      produtos.forEach(function(p){
        var item = document.createElement('div');
        var isSelected = selecionados[bocaAtiva] === p.id;
        item.style.cssText =
          'padding:10px 14px;border-radius:8px;cursor:pointer;font-size:.78rem;font-weight:600;'
          +'transition:all .15s;display:flex;align-items:center;gap:8px;'
          + (isSelected
            ? 'background:rgba(0,217,166,.15);border:1px solid #00d9a6;color:#00d9a6;'
            : 'background:#070d1a;border:1px solid rgba(0,217,166,.08);color:#dde6f0;');

        item.innerHTML =
          '<span style="font-size:1rem;">'+(isSelected?'✅':'🧪')+'</span>'
          +'<span>'+p.nome+'</span>';

        item.addEventListener('mouseenter', function(){
          if(!isSelected) item.style.background = 'rgba(0,217,166,.06)';
        });
        item.addEventListener('mouseleave', function(){
          if(!isSelected) item.style.background = '#070d1a';
        });
        item.addEventListener('click', function(){
          selecionados[bocaAtiva] = p.id;
          bocaAtiva = null; // volta para visão geral
          renderBocas();
          renderProdutos();
          updateResumo();
          syncInlines();
        });

        grid.appendChild(item);
      });
    }

    /* ── Resumo ──────────────────────────────────────────── */
    function updateResumo(){
      var el = document.getElementById('bocas-resumo');
      var total = compartimentos.length;
      var sel = Object.keys(selecionados).length;
      el.textContent = sel + ' de ' + total + ' bocas com produto';
    }

    /* ── Helpers ─────────────────────────────────────────── */
    function getProdutoNome(id){
      var p = produtos.find(function(x){ return x.id === id; });
      return p ? p.nome : '';
    }

    /* ── Sincronizar com Inline Django ───────────────────── */
    function syncInlines(){
      var prefix = 'carga_compartimentos';
      var totalForms = document.getElementById('id_'+prefix+'-TOTAL_FORMS');
      if(!totalForms) return;

      // Remover inputs gerados anteriormente pelo JS
      document.querySelectorAll('.synced-inline').forEach(function(el){ el.remove(); });

      // Marcar inlines originais do Django para deleção
      var existingRows = document.querySelectorAll('tr.dynamic-cargacompartimento, .dynamic-'+prefix);
      existingRows.forEach(function(row){
        var delInput = row.querySelector('input[id$="-DELETE"]');
        if(delInput){ delInput.checked = true; delInput.value = 'on'; }
        row.style.display = 'none';
      });

      var keys = Object.keys(selecionados);
      var initialForms = document.getElementById('id_'+prefix+'-INITIAL_FORMS');
      var initial = initialForms ? parseInt(initialForms.value) || 0 : 0;
      var startIdx = initial;

      keys.forEach(function(compId, i){
        var idx = startIdx + i;
        var formHtml =
          '<input type="hidden" name="'+prefix+'-'+idx+'-compartimento" value="'+compId+'">'
          +'<input type="hidden" name="'+prefix+'-'+idx+'-produto" value="'+selecionados[compId]+'">'
          +'<input type="hidden" name="'+prefix+'-'+idx+'-id" value="">'
          +'<input type="hidden" name="'+prefix+'-'+idx+'-carga" value="">';
        var div = document.createElement('div');
        div.style.display = 'none';
        div.innerHTML = formHtml;
        div.className = 'synced-inline';
        totalForms.parentNode.appendChild(div);
      });

      totalForms.value = startIdx + keys.length;
    }

    /* ── Esconder o inline padrão (manter funcional) ─────── */
    var inlineGrp = document.querySelector('.inline-group');
    if(inlineGrp){
      inlineGrp.style.display = 'none';
    }

    /* Se já tem valor de caminhão (edição), carregar */
    if(caminhaoSelect.value){
      lastCaminhaoVal = '';
      setTimeout(onCaminhaoChange, 500);
    }

    /* Animação fade */
    var style = document.createElement('style');
    style.textContent = '@keyframes fadeSlide{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}';
    document.head.appendChild(style);
  });
})();
