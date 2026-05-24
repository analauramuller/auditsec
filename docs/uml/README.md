# Diagramas UML - PSI

## Arquivos

- `use-case.puml` - casos de uso do auditor
- `class-diagram.puml` - classes principais e services

## Gerar PNG

Com Docker (PlantUML):

```bash
docker run --rm -v "$(pwd):/data" plantuml/plantuml -tpng /data/use-case.puml /data/class-diagram.puml
```

Com extensao PlantUML no VS Code/Cursor: abrir o `.puml` e exportar.

Os PNG gerados podem ser incluidos na apresentacao do PSI (25-26/maio).
