**Atualizações automáticas de plataformas de serviços por detecção instantânea  de mudanças em especificações de API**

Suellen Batista Dias¹\*; Vinícius Santos Andrade 2

1 Bacharel em Comunicação Social, Tecnóloga Superior em Desenvolvimento e Análise de Software. Avenida Las Heras, 2905 – Palermo; 1425   Ciudad Autónoma de Buenos Aires, Capital Federal, Argentina   
2 Nome da Empresa ou Instituição (opcional). Titulação ou função ou departamento. Endereço completo (pessoal ou profissional) – Bairro; 00000-000    Cidade, Estado, País  
\*autor correspondente: nome@email.com

**Atualizações automáticas de plataformas de serviços por detecção instantânea  de mudanças em especificações de API**

**Introdução**  
	  
O crescimento da chamada *Cloud Computing* é um fenômeno que vem sendo observado há mais de uma década e tem revolucionado a Tecnologia da Informação. Neste contexto, o papel dos chamados PaaS (*Platform as a Service)* ganham crescente destaque. Graças a essas tecnologias, desenvolver, hospedar e manter aplicações altamente escaláveis se tornou mais fácil e acessível.   
Diversas ferramentas digitais passam a estar disponíveis através de integrações cada vez mais simples. A necessidade de uma equipe altamente qualificada para gerir a comunicação entre sistemas diferentes vem sendo substituída por plataformas que permitem que usuários cada vez mais leigos possam criar rotinas de trabalho complexas, em alguns casos sem nenhuma linha de código.  
A Inteligência Artificial também encontra nesse tipo de plataforma um ambiente ideal para brilhar. A chamada *Agentic AI*, por exemplo, está entre as últimas tendências no mundo *Tech* e inclui agentes que planejam e executam fluxos de trabalho, assistentes pessoais e agentes de negócio com lógica autônoma. De acordo com Liu (2023), A *Agentic AI* se beneficia da integração de serviços, rapidez e escalabilidade e da abstração da infraestrutura oferecida pelos PaaS.   
O foco deste trabalho recairá sobre PaaS que oferecem acesso centralizado a vários tipos de *SaaS* (*Software as a Service*) para a geração de fluxos de ações relacionados a processos corporativos. Um desafio observado nesse contexto é acompanhar o ritmo da constante mudança dos serviços oferecidos, permitindo que os clientes possam acessar, através da plataforma, as últimas funcionalidades oferecidas pelo *SaaS*, em suas versões mais atualizadas.  
Os *SaaS* normalmente utilizam uma *API Specification*, ou *API Spec*, para definir como outros sistemas devem modelar suas requisições para que a comunicação se dê corretamente. As *API Specs* também podem informar modelos de resposta, indicações de segurança, exemplos de dados e explicação dos conceitos utilizados pelo software. Esses documentos normalmente seguem padrões reconhecidos, como o *OAS*.   
A proposta do presente estudo será, portanto, a detecção de mudanças nas *API Spec* dos serviços e a subsequente geração e disponibilização automática das novas versões para o cliente da Plataforma.

**Implementação de Algoritmo**

Para demonstrar esse processo, será utilizada a modalidade de pesquisa conhecida como Pesquisa-Ação. Um protótipo simulará a detecção automática de mudanças na especificação da *API* de um determinado *SaaS (Github)* e enviará uma notificação à Plataforma para que esta gere uma versão compatível com as últimas atualizações.   
A fim de melhor delinear o escopo deste trabalho, os processos internos e a infraestrutura da plataforma serão totalmente abstraídos desta pesquisa.  
Vale ressaltar que a solução aqui apresentada consiste de uma Prova de Conceito, ou PoC (do inglês *Proof of Concept*), e, desta forma, não será implementada em ambiente produtivo. Tampouco abarcará coleta de dados de usuários ou métricas comparativas de desempenho em um cenário real. A avaliação terá como base os aspectos técnicos e conceituais da proposta.   
	O desenvolvimento utilizará ferramentas como [*OpenAPI-diff*](https://github.com/OpenAPITools/openapi-diff), para monitorar as versões de *API Specs*. A partir da detecção de mudanças significativas, serão enviadas notificações à plataforma, por *webhooks*. O projeto estará escrito majoritariamente em *Python* e seguirá o padrão arquitetural orientado a eventos. 

Especificação de API do *GitHub*   
	  
A escolha do GitHub vem da sua relevância e popularidade entre a comunidade de desenvolvedores e a facilidade para obter credenciais gratuitas para a geração dos testes.   
Além do GitHub, o quadro abaixo ilustra outros exemplos de SaaS que publicam a versão oficial de sua API Specification em um repositório. Essa forma de disponibilização permite que mudanças sejam periodicamente monitoradas. A Tabela 1 cita três SaaS, que também poderiam ter sido utilizados neste projeto, com o link para o repositório de publicação de suas API Specs. 


| SaaS | Categoria	 | Repositório de Specs |
| :---- | :---- | :---- |
| [Stripe](https://stripe.com/en-br/payments) | Pagamentos Online | [stripe/openapi](https://github.com/stripe/openapi) |
| [Twilio](https://www.twilio.com/en-us) | Engajamento de Clientes | [twilio/twilio-oai](https://github.com/twilio/twilio-oai) |
| [Microsoft Azure](https://learn.microsoft.com/en-us/azure/?product=popular)	 | Serviços de Cloud  | [Azure/azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) |

Estratégia de notificação

Duas formas de implementação foram consideradas para implementar as notificações de atualização. Por um lado, serviços de mensageria são opções robustas e confiáveis, que oferecem processamento assíncrono, controle de fluxo e permitem múltiplos consumidores para os eventos (no caso, a notificação). Tais serviços, cujo principais exemplos seriam o RabbitMQ e Kafka, oferecem grande estabilidade para aplicações Web com grande número de usuários, conforme apontam Xianghua et al. (2018).  
A segunda alternativa é o uso de Webhooks. Tratam-se basicamente de requisições HTTP, de simples entendimento e implementação. Eles permitem a entrega de notificações a outros serviços em tempo real, e são muito usados para a manutenção de dados sincronizados e  para disparar fluxos de trabalhos automatizados. Segundo Vijayakumar e Chokkalingam (2017), os webhooks são grandes facilitadores de integração com serviços externos. 	  
A implementação deste projeto, dada sua natureza de PoC, priorizará a solução mais direta. O uso de webhooks será suficiente para disparar as notificações necessárias e o fará sem a necessidade de filas ou servidores intermediários. O volume dos eventos também é reduzido, uma vez que as atualizações de API Spec para github costumam ocorrer, não mais que duas vezes por semana.

**Resultados Preliminares**

A visão deste projeto é que ele seja uma peça que integra, de um lado, os *SaaS*’s e suas especificações de API, e de outro, uma plataforma que se conecta a, ou diretamente hospeda, sistemas interessados em interagir com os serviços oferecidos pelos *Software as Services* monitorados. A orquestração de todos esses elementos, por uma limitação de escopo, não será detalhada neste trabalho. A Imagem 2 extrapola a implementação apresentada neste projeto e apresenta uma visão mais ampla dos componentes envolvidos no *end to end* da solução proposta. 

**Conclusão(ões) ou Considerações Finais**

**Referências**

Cusumano, M. A. Cloud computing and SaaS as new computing platforms. Communications of the ACM, v. 53, n. 4, p. 27–29, 2010\. Disponível em: [https://doi.org/10.1145/1721654.1721667](https://doi.org/10.1145/1721654.1721667). Acesso em: 28 mar. 2025\.

Liu, Yuzhuo et al. *Agentic AI*: A Survey. \[S.l.\]: arXiv, 2023\. Disponível em: [https://arxiv.org/abs/2310.02207](https://arxiv.org/abs/2310.02207). Acesso em: 28 mar. 2025\.

Shvets, A. Dive into design patterns. \[S.l.\]: Refactoring.Guru, 2018\.

Yasrab, R. Platform-as-a-Service (PaaS): The next hype of cloud computing. ResearchGate, 2018\. Disponível em: [https://www.researchgate.net/publication/325973616\_Platform-as-a-Service\_PaaS\_The\_Next\_Hype\_of\_Cloud\_Computing](https://www.researchgate.net/publication/325973616_Platform-as-a-Service_PaaS_The_Next_Hype_of_Cloud_Computing). Acesso em: 28 mar. 2025\.

Hong, X., Yang, H., & Kim, Y. (2018). Performance Analysis of RESTful API and RabbitMQ for Microservice Web Application. 2018 International Conference on Information and Communication Technology Convergence (ICTC), 257-259. https://doi.org/10.1109/ICTC.2018.8539409.Acesso em: 30 maio 2025

Vijayakumar, K., & Chokkalingam, A. (2017). Continuous security assessment of cloud based applications using distributed hashing algorithm in SDLC. *Cluster Computing*, 22, 10789 \- 10800\. [https://doi.org/10.1007/s10586-017-1176-x](https://doi.org/10.1007/s10586-017-1176-x).

**Apêndice ou Anexo** (opcional)

